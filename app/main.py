from fastapi import FastAPI

app = FastAPI(
    title="Assessor IA",
    description="Assessor financeiro e de agenda com langchain e langgraph",
    version="0.1.0"
)

@app.get("/healt")
def health_check() -> dict:
    """Rota de verificação de saúde da aplicação."""
    return {"status": "ok"}