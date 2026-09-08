from langchain.tools import tool
from app.vectorstore import qdrant, gerar_embedding, garantir_colecao, COLLECTION_FAQ


@tool("faq_retriever")
def search_faq(question: str) -> str:
    """Busca no FAQ oficial os trechos mais relevantes para responder a pergunta."""
    garantir_colecao(COLLECTION_FAQ)
    vetor = gerar_embedding(question)

    resultados = qdrant.query_points(
        collection_name=COLLECTION_FAQ,
        query=vetor,
        limit=6,
    )

    if not resultados.points:
        return "Nenhum trecho relevante encontrado no FAQ."

    return "\n\n".join(
        ponto.payload["page_content"] for ponto in resultados.points if "page_content" in ponto.payload
    )
