"""
Cliente Qdrant e função de embedding — centralizados aqui.

Consumidores:
  - memoryMongo.py / memory.py → salva/busca resumos na collection "memoria_resumos"
  - tools/faq.py             → busca chunks do PDF na collection "faq_chunks"
  - perfil.py                → salva/busca preferências do perfil na collection "preferencias_perfil"
"""

from qdrant_client import QdrantClient, models
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import QDRANT_URL, QDRANT_API_KEY, GEMINI_API_KEY

COLLECTION_MEMORIA = "memoria_resumos"
COLLECTION_FAQ     = "faq_chunks"
COLLECTION_PERFIL  = "preferencias_perfil"
EMBEDDING_DIM      = 768

def _criar_qdrant_client() -> QdrantClient:
    """Tenta conectar ao Qdrant URL configurado. Se falhar, usa cliente em memória."""
    if QDRANT_URL and QDRANT_API_KEY and "localhost" not in QDRANT_URL:
        try:
            client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=3)
            client.get_collections()
            return client
        except Exception:
            pass

    if QDRANT_URL:
        try:
            client = QdrantClient(url=QDRANT_URL, timeout=3)
            client.get_collections()
            return client
        except Exception:
            pass

    return QdrantClient(location=":memory:")

qdrant = _criar_qdrant_client()

_embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview",
    google_api_key=GEMINI_API_KEY,
)

def garantir_colecao(collection_name: str) -> None:
    """Garante que a collection existe no Qdrant com a dimensão correta (768)."""
    try:
        colecoes = [c.name for c in qdrant.get_collections().collections]
        if collection_name in colecoes:
            info = qdrant.get_collection(collection_name)
            params = getattr(getattr(info, "config", None), "params", None)
            vec_params = getattr(params, "vectors", None)
            dim = getattr(vec_params, "size", None) if vec_params else None
            if dim and dim != EMBEDDING_DIM:
                qdrant.delete_collection(collection_name)
                colecoes.remove(collection_name)

        if collection_name not in colecoes:
            qdrant.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=EMBEDDING_DIM, distance=models.Distance.COSINE)
            )
    except Exception as e:
        print(f"[Qdrant Init Warning {collection_name}] {e}")

def gerar_embedding(texto: str) -> list[float]:
    """Gera um vetor de 768 dimensões para o texto informado."""
    return _embeddings.embed_query(texto, output_dimensionality=EMBEDDING_DIM)

def gerar_embeddings_batch(textos: list[str]) -> list[list[float]]:
    """Gera embeddings para uma lista de textos de uma vez (mais eficiente)."""
    return _embeddings.embed_documents(textos, output_dimensionality=EMBEDDING_DIM)
