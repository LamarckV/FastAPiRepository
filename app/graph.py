import re
from typing import Annotated, Any, TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, MessagesState, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from app.tools.financeiro import TOOLS
from app.tools.faq import search_faq
from app.guardrail import anonimizar_entrada, guardrail_entrada, guardrail_saida
from langchain_core.messages import RemoveMessage
from app.llm import llm, llmRapido
from app.prompts import (
    ROUTER_PROMPT_COMPLETO,
    FINANCEIRO_PROMPT_COMPLETO,
    AGENDA_PROMPT_COMPLETO,
    ORQUESTRADOR_PROMPT_COMPLETO,
    FAQ_PROMPT_COMPLETO,
)

routerMemory = MemorySaver()


def extract_text(content: Any) -> str:
    """Return only user-facing text from LangChain/provider content blocks."""
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                block_text = block.get("text")
                if isinstance(block_text, str):
                    parts.append(block_text)
            else:
                block_text = getattr(block, "text", None)
                if isinstance(block_text, str):
                    parts.append(block_text)
        text = "\n".join(parts)
    else:
        text = str(content) if content is not None else ""

    # 1. Remove blocos <think>...</think> completos
    text = re.sub(r"<think\b[^>]*>.*?</think>\s*", "", text, flags=re.IGNORECASE | re.DOTALL)
    # 2. Remove blocos <think> sem tag de fechamento até o fim do texto
    text = re.sub(r"<think\b[^>]*>.*$", "", text, flags=re.IGNORECASE | re.DOTALL)

    return text.strip()

# Roteador
routerApp = create_agent(
    model=llmRapido,
    system_prompt=ROUTER_PROMPT_COMPLETO,
    checkpointer=routerMemory,
)

# Especialistas
financeiroApp = create_agent(
    model=llm,
    system_prompt=FINANCEIRO_PROMPT_COMPLETO,
    tools=TOOLS,
)

agendaApp = create_agent(
    model=llm,
    system_prompt=AGENDA_PROMPT_COMPLETO,
)

orquestradorApp = create_agent(
    model=llmRapido,
    system_prompt=ORQUESTRADOR_PROMPT_COMPLETO,
)

faqApp = create_agent(
    model=llm,
    system_prompt=FAQ_PROMPT_COMPLETO,
    tools=[search_faq],
)

# Estado
class Estado(MessagesState):
    agentes: Annotated[list[str], "Lista dos agentes chamados durante o fluxo."]
    rota: str
    mapa_pii: dict  # tokens -> valores originais gerados na anonimização

# Nós
def no_roteador(estado: Estado) -> dict:
    saida = routerApp.invoke({"messages": list(estado["messages"])})
    texto = extract_text(saida["messages"][-1].content)

    if "ROUTE=" not in texto:
        return {
            "agentes": estado["agentes"] + ["roteador"],
            "rota": "fim",
            "messages": [{"role": "assistant", "content": texto}],
        }

    rota = "fim"
    for linha in texto.splitlines():
        if linha.startswith("ROUTE="):
            rota = linha.split("=", 1)[1].strip()
            break

    return {
        "agentes": estado["agentes"] + ["roteador", rota],
        "rota": rota,
    }


def no_guardrail_entrada(estado: Estado) -> dict:
    pergunta_usuario = estado["messages"][-1].content
    texto_anonimizado, mapa_pii = anonimizar_entrada(pergunta_usuario)
    resposta_guardrail = guardrail_entrada(texto_anonimizado)

    if resposta_guardrail["bloqueado"]:
        return {
            "rota": "fim",
            "agentes": estado["agentes"] + ["guardrail_entrada"],
            "messages": [{"role": "assistant", "content": resposta_guardrail["mensagem"]}],
        }
    else:
        return {
            "mapa_pii": mapa_pii,
            "agentes": estado["agentes"] + ["guardrail_entrada"],
            "messages": [
                RemoveMessage(id=estado["messages"][-1].id),
                {"role": "human", "content": texto_anonimizado}
            ],
        }

def no_guardrail_saida(estado: Estado) -> dict:
    resposta_orquestrador = extract_text(estado["messages"][-1].content)
    mapa_pii = estado["mapa_pii"]
    resposta_final = guardrail_saida(resposta_orquestrador, mapa_pii)

    return {
        "messages": [{"role": "assistant", "content": resposta_final["conteudo"]}],
        "agentes": estado["agentes"] + ["guardrail_saida"],
    }


def no_orquestrador(estado: Estado) -> dict:
    last_content = estado["messages"][-1].content

    orquestration_prompt = (
        "Com base na estrutura JSON do agente especialista abaixo, gere uma resposta clara, "
        "amigável e direta para o usuário em português (br):\n\n"
        f"{last_content}"
    )

    output = orquestradorApp.invoke({
        "messages": [{"role": "user", "content": orquestration_prompt}]
    })

    return {
        "agentes": estado["agentes"] + ["orquestrador"],
        "messages": [output["messages"][-1]],
    }

def decidir_especialista(estado: Estado) -> str:
    rota = estado.get("rota", "fim")

    return rota if rota in (
        "financeiro",
        "agenda",
        "faq",
    ) else "fim"


def decidir_pos_guardrail_entrada(estado: Estado) -> str:
    if estado.get("messages", []) and estado.get("rota", "") == "fim":
        return "fim"
    return "roteador"

# Construção do grafo
grafo = StateGraph(Estado)

grafo.add_node("guardrail_entrada", no_guardrail_entrada)
grafo.add_node("roteador", no_roteador)
grafo.add_node("financeiro", financeiroApp)
grafo.add_node("agenda", agendaApp)
grafo.add_node("faq", faqApp)
grafo.add_node("orquestrador", no_orquestrador)
grafo.add_node("guardrail_saida", no_guardrail_saida)

grafo.set_entry_point("guardrail_entrada")
grafo.add_conditional_edges(
    "guardrail_entrada",
    decidir_pos_guardrail_entrada,
    {"roteador": "roteador", "fim": END},
)

grafo.add_conditional_edges(
    "roteador",
    decidir_especialista,
    {"financeiro": "financeiro", "agenda": "agenda", "faq": "faq", "fim": END},
)

grafo.add_edge("financeiro", "orquestrador")
grafo.add_edge("agenda", "orquestrador")
grafo.add_edge("orquestrador", "guardrail_saida")
grafo.add_edge("guardrail_saida", END)
grafo.add_edge("faq", "guardrail_saida")

memory = MemorySaver()
fluxo_agentes = grafo.compile(checkpointer=memory)

# Função principal

def executar_fluxo_assessor(pergunta_usuario: str, session_id: str) -> dict:
    estado_inicial = {
        "messages": [{"role": "human", "content": pergunta_usuario}],
        "agentes": [],
        "rota": "",
        "mapa_pii": {},
    }
    
    estado_final = fluxo_agentes.invoke(
        estado_inicial,
        config={"configurable": {"thread_id": session_id}},
    )

    print(f"[debug] agentes chamados: {estado_final.get('agentes')}")

    print(estado_final)  # debug temporário

    resposta = extract_text(estado_final["messages"][-1].content)
    return {
        "resposta": resposta,
        "agentes_chamados": estado_final.get("agentes", []),
    }

