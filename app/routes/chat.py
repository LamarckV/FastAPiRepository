from fastapi import APIRouter
from app.schemas import ChatRequest, ChatResponse
from app.graph import executar_fluxo_assessor

router = APIRouter(tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
def chat(requisition: ChatRequest) -> ChatResponse:
    """Recieve a message from the user and return a response from the AI model."""
    result = executar_fluxo_assessor(requisition.question, requisition.session_id)
    return ChatResponse(response=result)