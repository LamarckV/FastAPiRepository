from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    """What the server send on POST /chat."""
    session_id: str = Field(..., examples=["id_user"])
    question: str = Field(..., min_length=1, examples=["Gastei 50 reais no mercado"])

class ChatResponse(BaseModel):
    """What the API will responde on POST /chat."""
    response: str
    agents_called: list[str] = Field(default_factory=list)

class SessionResponse(BaseModel):
    """Still not working - from step 6 to 3."""
    session_id: str
    resume: str | None = None