from fastapi import FastAPI
from app.routes import chat
from app.config import validate_config

for _problem in validate_config():
    print(f"[config] ATENTION: { _problem }")

app = FastAPI(  
    title="Assessor IA",
    description="Assessor financeiro e de agenda com langchain e langgraph",
    version="0.1.0"
)

@app.get("/healt")
def health_check() -> dict:
    """API health check endpoint. Returns a simple status message."""
    problem = validate_config()
    return {
            "status": "ok",
            "config_problems": problem,
        }

app.include_router(chat.router)
