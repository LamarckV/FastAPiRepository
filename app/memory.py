# memory_tools.py
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from pymongo import MongoClient
from datetime import datetime, timezone
from app.config import MONGODB_URI, MONGODB_DB, LL

client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB]
col_sessoes = db["sessoes"]


def salvar_turno(
    session_id: str,
    pergunta: str,
    resposta: str,
) -> None:
    """Persiste um turno concluído da sessão após a validação de saída."""
    agora = datetime.now(timezone.utc)

    col_sessoes.update_one(
        {"_id": session_id},
        {
            "$setOnInsert": {
                "session_id": session_id,
                "iniciada_em": agora,
                "resumo": "",
            },
            "$set": {
                "atualizada_em": agora,
            },
            "$inc": {"total_turnos": 1},
            "$push": {
                "mensagens": {
                    "$each": [
                        {"role": "user", "content": pergunta, "criada_em": agora},
                        {"role": "assistant", "content": resposta, "criada_em": agora},
                    ]
                }
            },
        },
        upsert=True,
    )

@tool
def buscar_historico(busca: str, config: RunnableConfig) -> str:
    """Consulta conversas ANTERIORES do usuário (sessões já encerradas).

    Use SOMENTE quando a resposta depende de algo dito numa conversa passada
    — preferências, decisões ou planos que o usuário mencionou antes.
    NÃO use para dados que estão no banco (gastos, saldos, eventos): para isso
    já existem as tools de consulta específicas como query_transactions, total_balance, daily_balance.

    Args:
        busca: assunto a procurar nos resumos das conversas anteriores.
    """
    session_id = config["configurable"]["thread_id"]   # injetado pelo main.py
    historico  = recuperar_historico(session_id, busca=busca, limite=3)

    if not historico:
        return "Nenhuma conversa anterior relevante encontrada."

    return "\n\n".join(
        f"[{h['iniciada_em']:%d/%m/%Y}] {h['resumo']}" for h in historico
    )






def recuperar_historico(session_id: str, busca: str = "", limite: int = 3) -> list[dict]:
    """
    Recupera resumos de sessões ANTERIORES (já encerradas) de um usuário.

    Estratégia: olha primeiro os resumos. Se houver termo de busca, filtra
    por ele; senão, traz as sessões mais recentes. As mensagens completas
    NÃO vêm aqui — para isso use recuperar_mensagens(doc_id).

    session_id : identifica o usuário (hoje fixo, depois dinâmico)
    busca      : termo opcional para filtrar resumos relevantes
    limite     : máximo de sessões retornadas (mais recentes primeiro)
    """
    # só sessões DESTE usuário que já têm resumo (= já encerradas)
    filtro = {"session_id": session_id}

    # se houver termo de busca, filtra resumos que o contenham (case-insensitive)
    if busca:
        filtro["resumo"] = {"$regex": busca, "$options": "i"}

    docs = (
        col_sessoes
        .find(filtro, {"resumo": 1, "iniciada_em": 1})  # projeção: sem mensagens
        .sort("iniciada_em", -1)                          # mais recentes primeiro
        .limit(limite)
    )

    return [
        {"doc_id": d["_id"], "iniciada_em": d["iniciada_em"], "resumo": d["resumo"]}
        for d in docs
    ]


def recuperar_mensagens(doc_id: str) -> list[dict]:
    """
    Busca o array completo de mensagens de um documento específico, pelo _id.
    Usada no passo 2 — só quando o resumo deu match e você precisa do detalhe
    literal da conversa. No futuro, o doc_id virá do Qdrant.
    """
    doc = col_sessoes.find_one({"_id": doc_id}, {"mensagens": 1})
    return doc["mensagens"] if doc else []


def obter_contexto_para_resumo(session_id: str, limite_mensagens: int = 12) -> tuple[str, list[dict]]:
    """Retorna o resumo vigente e os últimos turnos de uma sessão para o resumidor."""
    doc = col_sessoes.find_one(
        {"_id": session_id},
        {"resumo": 1, "mensagens": {"$slice": -limite_mensagens}},
    )

    if not doc:
        return "", []

    return doc.get("resumo", ""), doc.get("mensagens", [])


def atualizar_resumo(session_id: str, resumo: str) -> None:
    """Persiste o resumo consolidado da sessão já existente."""
    col_sessoes.update_one(
        {"_id": session_id},
        {"$set": {"resumo": resumo, "atualizada_em": datetime.now(timezone.utc)}},
    )


TOOLS_MEMORIA = [buscar_historico]