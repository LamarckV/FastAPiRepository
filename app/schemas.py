from pydantic import AliasChoices, BaseModel, ConfigDict, Field

class ChatRequest(BaseModel):
    """Payload aceito pelo endpoint POST /chat."""
    model_config = ConfigDict(populate_by_name=True)

    session_id: str = Field(..., examples=["id_user"])
    pergunta: str = Field(
        ...,
        min_length=1,
        validation_alias=AliasChoices("pergunta", "question"),
        examples=["Gastei 50 reais no mercado"],
    )

class ChatResponse(BaseModel):
    """Resposta entregue ao frontend."""
    resposta: str
    agentes_chamados: list[str] = Field(default_factory=list)

class SessionResponse(BaseModel):
    """Still not working - from step 6 to 3."""
    session_id: str
    resume: str | None = None
