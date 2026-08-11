from fastapi import APIRouter
from app.schemas import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
def chat(requisition: ChatRequest) -> ChatResponse:
    """Recieve a message from the user and return a response from the AI model."""
    return ChatResponse(
        response=(
            f"Recieved yout message on session '{requisition.session_id}':"
            f"\"{requisition.question}\". The graph isnt working yet on this rout"
        ),
        agents_called=["echo_test"],
    )