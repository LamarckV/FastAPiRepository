import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pymongo import MongoClient
from qdrant_client import models
from app.config import MONGODB_URI
from app.schemas import PerfilRequest
from app.vectorstore import qdrant, gerar_embedding, garantir_colecao, COLLECTION_PERFIL, EMBEDDING_DIM

# MongoDB Setup
_mongo = MongoClient(MONGODB_URI)
db = _mongo["assessor"]
col_perfil = db["perfil"]
col_perfil.create_index("user_id", unique=True)

def _garantir_colecao_perfil() -> None:
    garantir_colecao(COLLECTION_PERFIL)

def salvar_perfil(dados: PerfilRequest) -> Dict[str, Any]:
    """
    Grava ou atualiza os dados estruturados no MongoDB e o texto livre de preferências no Qdrant.
    Salvar de novo com o mesmo user_id substitui o cadastro anterior nos dois bancos.
    """
    user_id = dados.user_id

    # 1. MongoDB: Grava/Atualiza dados estruturados
    doc_perfil = {
        "user_id": user_id,
        "renda_mensal": dados.renda_mensal,
        "objetivo": dados.objetivo,
        "tolerancia_risco": dados.tolerancia_risco,
        "preferencias": dados.preferencias,
        "atualizado_em": datetime.now(timezone.utc)
    }
    
    col_perfil.update_one(
        {"user_id": user_id},
        {"$set": doc_perfil},
        upsert=True
    )

    # 2. Qdrant: Grava/Atualiza preferências com busca semântica
    _garantir_colecao_perfil()

    # Remove vetores anteriores do mesmo user_id para garantir substituição limpa
    try:
        qdrant.delete(
            collection_name=COLLECTION_PERFIL,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[models.FieldCondition(key="user_id", match=models.MatchValue(value=user_id))]
                )
            )
        )
    except Exception:
        pass

    # Indexa o novo texto de preferências se houver conteúdo
    if dados.preferencias.strip():
        vetor = gerar_embedding(dados.preferencias.strip())
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{user_id}_preferencias"))
        qdrant.upsert(
            collection_name=COLLECTION_PERFIL,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=vetor,
                    payload={
                        "user_id": user_id,
                        "texto": dados.preferencias.strip()
                    }
                )
            ]
        )

    return {
        "user_id": dados.user_id,
        "renda_mensal": dados.renda_mensal,
        "objetivo": dados.objetivo,
        "tolerancia_risco": dados.tolerancia_risco,
        "preferencias": dados.preferencias,
    }

def obter_perfil_mongodb(user_id: str) -> Optional[Dict[str, Any]]:
    """Consulta os dados estruturados do perfil do usuário no MongoDB."""
    return col_perfil.find_one({"user_id": user_id}, {"_id": 0})

def buscar_preferencias_qdrant(user_id: str, query: str = "", limite: int = 3) -> List[str]:
    """Realiza busca semântica nas preferências do usuário no Qdrant."""
    if not query.strip():
        query = "preferências e restrições de investimento"

    try:
        _garantir_colecao_perfil()
        vetor_busca = gerar_embedding(query)

        resultado = qdrant.query_points(
            collection_name=COLLECTION_PERFIL,
            query=vetor_busca,
            query_filter=models.Filter(
                must=[models.FieldCondition(key="user_id", match=models.MatchValue(value=user_id))]
            ),
            limit=limite
        )
        return [p.payload["texto"] for p in resultado.points if "texto" in p.payload]
    except Exception as e:
        print(f"[Qdrant Search Warning] {e}")
        return []
