from pydantic import AliasChoices, BaseModel, ConfigDict, Field

class ChatRequest(BaseModel):
    """Payload aceito pelo endpoint POST /chat."""
    model_config = ConfigDict(populate_by_name=True)

    session_id: str = Field(..., examples=["550e8400-e29b-41d4-a716-446655440000"])
    user_id: str = Field(default="usuario_teste", description="Identifica o usuário de forma estável entre sessões.")
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
class PerfilRequest(BaseModel):
    """Payload de gravação/atualização do perfil do usuário."""
    user_id: str = Field(..., min_length=1, description="Identificador estável do usuário")
    renda_mensal: float = Field(..., gt=0, description="Renda mensal maior que zero")
    objetivo: str = Field(..., min_length=1, description="Frase curta de objetivo")
    tolerancia_risco: str = Field(..., description="Somente 'baixa', 'media' ou 'alta'")
    preferencias: str = Field(..., description="Texto livre de preferências para busca semântica")

    def model_post_init(self, __context):
        if not self.user_id.strip():
            raise ValueError("user_id não pode ser vazio")
        if not self.objetivo.strip():
            raise ValueError("objetivo não pode ser vazio")
        if self.tolerancia_risco not in ("baixa", "media", "alta"):
            raise ValueError("tolerancia_risco deve ser 'baixa', 'media' ou 'alta'")

class PerfilResponse(PerfilRequest):
    """Resposta com o perfil gravado."""
    pass
