from dotenv import load_dotenv
import os
from pathlib import Path


BASE_DIR     = Path(__file__).resolve().parent.parent
DATA_DIR     = BASE_DIR / "data"
FRONTEND_DIR = BASE_DIR / "frontend"

FAQ_PDF_PATH = DATA_DIR / "FAQ_assessor_v1.1.pdf"

load_dotenv(BASE_DIR / ".env")          

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY   = os.getenv("GROQ_API_KEY")
DATABASE_URL   = os.getenv("DATABASE_URL")
MONGODB_URI    = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

OBRIGATORIES = {
    "GEMINI_API_KEY": GEMINI_API_KEY,
    "GROQ_API_KEY":   GROQ_API_KEY,
    "DATABASE_URL":   DATABASE_URL,
    "MONGODB_URI":    MONGODB_URI,
}


def validate_config() -> list[str]:
    """Devolve a lista de problemas de configuração (vazia = tudo certo)."""
    problems = []
    for nome, valor in OBRIGATORIES.items():
        if not valor:
            problems.append(f"Variável ausente no .env: {nome}")
    if not FAQ_PDF_PATH.exists():
        problems.append(f"PDF do FAQ não encontrado em: {FAQ_PDF_PATH}")
    return problems