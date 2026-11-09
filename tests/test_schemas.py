import pytest
from pydantic import ValidationError

from app.schemas import ChatRequest, ChatResponse, PerfilRequest


@pytest.mark.parametrize("question_field", ["pergunta", "question"])
def test_chat_request_accepts_question_field_aliases(question_field):
    payload = {"session_id": "session-123", question_field: "Quanto gastei?"}

    request = ChatRequest.model_validate(payload)

    assert request.session_id == "session-123"
    assert request.pergunta == "Quanto gastei?"
    assert request.user_id == "usuario_teste"


def test_chat_request_requires_session_id():
    with pytest.raises(ValidationError):
        ChatRequest.model_validate({"pergunta": "Quanto gastei?"})


@pytest.mark.parametrize("question", ["", None])
def test_chat_request_rejects_empty_question(question):
    with pytest.raises(ValidationError):
        ChatRequest.model_validate({"session_id": "session-123", "pergunta": question})


def test_chat_response_agent_list_default_is_independent():
    first = ChatResponse(resposta="Olá")
    second = ChatResponse(resposta="Tudo bem")

    first.agentes_chamados.append("router")

    assert first.agentes_chamados == ["router"]
    assert second.agentes_chamados == []


def test_perfil_request_accepts_valid_baseline():
    perfil = PerfilRequest(
        user_id="usuario-123",
        renda_mensal=4200,
        objetivo="guardar para uma viagem",
        tolerancia_risco="media",
        preferencias="Prefere investimentos conservadores.",
    )

    assert perfil.user_id == "usuario-123"
    assert perfil.renda_mensal == 4200
    assert perfil.tolerancia_risco == "media"


@pytest.mark.parametrize("income", [0, -0.01])
def test_perfil_request_rejects_nonpositive_income(income):
    with pytest.raises(ValidationError):
        PerfilRequest(
            user_id="usuario-123",
            renda_mensal=income,
            objetivo="guardar para uma viagem",
            tolerancia_risco="media",
            preferencias="Prefere investimentos conservadores.",
        )


def test_perfil_request_rejects_invalid_risk_level():
    with pytest.raises(ValidationError):
        PerfilRequest(
            user_id="usuario-123",
            renda_mensal=4200,
            objetivo="guardar para uma viagem",
            tolerancia_risco="extrema",
            preferencias="Prefere investimentos conservadores.",
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [("user_id", "   "), ("objetivo", "   ")],
)
def test_perfil_request_rejects_whitespace_only_required_text(field, value):
    payload = {
        "user_id": "usuario-123",
        "renda_mensal": 4200,
        "objetivo": "guardar para uma viagem",
        "tolerancia_risco": "media",
        "preferencias": "Prefere investimentos conservadores.",
    }
    payload[field] = value

    with pytest.raises(ValidationError):
        PerfilRequest.model_validate(payload)
