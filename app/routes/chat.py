from fastapi import APIRouter
from app.schemas import ChatRequest, ChatResponse
from app.graph import executar_fluxo_assessor

router = APIRouter(tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
def chat(requisition: ChatRequest) -> ChatResponse:
    """Recieve a message from the user and return a response from the AI model."""
    question = requisition.question
    session_id = requisition.session_id

    result = executar_fluxo_assessor(question, session_id)

    lastLine = result.strip().splitlines()
    response = lastLine[-1] if lastLine else ""

    return ChatResponse(response=response)