from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import GEMINI_API_KEY, GROQ_API_KEY

# =============================================================================
# LLMs
# =============================================================================

llmGuard = ChatGroq(
    model="qwen/qwen3.6-27b", 
    temperature=0, 
    api_key=GROQ_API_KEY
)
llm_gemini = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    top_p=0.95,
    google_api_key=GEMINI_API_KEY
)

llm_groq = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.7,
    top_p=0.95,
    api_key=GROQ_API_KEY,
)

llm = llm_gemini.with_fallbacks([llm_groq])

llmRapido = ChatGroq(
    model="qwen/qwen3.6-27b",
    temperature=0,
    api_key=GROQ_API_KEY,
)

_llm_resumo = ChatGroq(
    model="qwen/qwen3.6-27b",
    temperature=0,
    api_key=GROQ_API_KEY
)
