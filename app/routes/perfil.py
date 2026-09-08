from fastapi import APIRouter, status
from app.schemas import PerfilRequest, PerfilResponse
from app.perfil import salvar_perfil

router = APIRouter(tags=["perfil"])

@router.post("/perfil", response_model=PerfilResponse, status_code=status.HTTP_200_OK)
def salvar_perfil_endpoint(requisition: PerfilRequest) -> PerfilResponse:
    """Recebe e grava/atualiza o perfil do usuário no MongoDB e Qdrant."""
    resultado = salvar_perfil(requisition)
    return PerfilResponse(**resultado)
