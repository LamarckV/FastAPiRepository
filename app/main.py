from fastapi import FastAPI
from app.routes import chat
from app.config import validate_config, FRONTEND_DIR
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# frontend

if (FRONTEND_DIR / "index.html").exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    @app.get("?", tags=["infra"])
    def raiz() -> dict:
        return{
            "mensagem": "API do assessor no ar. o frontend ainda n foi criado"
        }