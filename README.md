# 🤖 Assessor.AI — Intelligent Financial & Agenda AI Assistant

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-005587?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/LangChain-121212?style=for-the-badge&logo=chainlink&logoColor=white" alt="LangChain" />
  <img src="https://img.shields.io/badge/LangGraph-FF6F00?style=for-the-badge&logo=diagram&logoColor=white" alt="LangGraph" />
  <img src="https://img.shields.io/badge/Qdrant-DA291C?style=for-the-badge&logo=qdrant&logoColor=white" alt="Qdrant" />
  <img src="https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Google_Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini" />
</p>

**Assessor.AI** is a state-of-the-art conversational AI system designed to act as a personal financial advisor and schedule manager. Built on top of **FastAPI**, **LangGraph**, **Qdrant Vector Database**, and **MongoDB**, it combines structured database storage with semantic vector search, long-term memory across sessions, and automated safety guardrails.

---

## 🌟 Key Features

### 🧠 1. Multi-Agent Orchestration (LangGraph)
- **Router Agent:** Classifies user intent and routes traffic dynamically to specialists (`financeiro`, `agenda`, `faq`), while directly handling greetings and out-of-scope inquiries.
- **Financial Specialist:** Manages balance checks, transaction additions, category lookups, and provides financial advice anchored on the user's registered profile.
- **Agenda Specialist:** Handles calendar events, schedule availability, and appointment planning.
- **FAQ RAG Specialist:** Performs retrieval-augmented generation on official documentation via vector search.
- **Orchestrator Agent:** Converts structured JSON outputs from specialist agents into natural, user-friendly responses.

### 👤 2. User Financial Profile & Hybrid Persistence
- **Structured Storage (MongoDB):** Persists quantitative profile data (`user_id`, `renda_mensal`, `objetivo`, `tolerancia_risco`).
- **Semantic Preferences (Qdrant):** Embeds free-text preferences using 768-dimensional Gemini embeddings for semantic retrieval (e.g., matching *"no aggressive investments"* to queries about *"crypto"* without exact keyword matches).
- **Strict Validation:** Rejects invalid payloads (e.g., non-positive income or invalid risk tiers) at the API boundary using Pydantic.

### 📚 3. Long-Term Semantic Memory
- Stores session summaries in Qdrant with `user_id` multitenant isolation.
- Allows the AI assistant to remember past context across sessions without keyword limitations.

### 🛡️ 4. Safety & Compliance Guardrails
- **Input Guardrail:** Anonymizes Personally Identifiable Information (PII) such as CPF, emails, and phone numbers before LLM processing.
- **Output Guardrail:** Inspects generated responses for financial compliance (CVM/ANBIMA regulations).

---

## 📁 Repository Structure

```
.
├── app/
│   ├── config.py             # Environment configuration & validation
│   ├── graph.py              # LangGraph state machine & node orchestration
│   ├── guardrail.py          # Input/Output PII anonymization & compliance
│   ├── ingest_faq.py         # PDF text chunking & Qdrant vector indexing
│   ├── llm.py                # LLM model definitions (Gemini 2.5 Flash, Groq Qwen/GPT-OSS)
│   ├── main.py               # FastAPI entry point & static file routing
│   ├── memoryMongo.py        # MongoDB session persistence & Qdrant memory search
│   ├── perfil.py             # Profile service (MongoDB + Qdrant sync)
│   ├── prompts.py            # System prompts for Router, Specialists & Orchestrator
│   ├── schemas.py            # Pydantic data contracts (Chat & Profile)
│   ├── vectorstore.py        # Qdrant client connection & embedding utilities
│   ├── routes/
│   │   ├── chat.py           # POST /chat endpoint
│   │   └── perfil.py         # POST /perfil endpoint
│   └── tools/
│       ├── db.py             # PostgreSQL connection pool
│       ├── faq.py            # Qdrant-backed FAQ retriever tool
│       └── financeiro.py     # Financial tools (transactions, balance, profile lookup)
├── data/
│   └── FAQ_assessor_v1.1.pdf # Official PDF document for FAQ indexing
├── frontend/
│   ├── app.js                # Chat interface logic
│   ├── index.html            # Main Chat console
│   ├── perfil.css            # Profile page styling
│   ├── perfil.html           # Dedicated User Profile web interface
│   ├── perfil.js             # Profile form POST handler
│   └── style.css             # Global dark theme tokens
├── JUSTIFICATIVA.md          # Technical architectural rationale
└── README.md                 # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed:
- **Python 3.10+**
- **MongoDB** (Local instance or MongoDB Atlas URI)
- **PostgreSQL** (Aiven Cloud or local Postgres)
- **Qdrant** (Qdrant Cloud URL or local in-memory/disk instance)
- API Keys for **Google Gemini** and **Groq**

---

### 1. Installation

Clone the repository and navigate into the project directory:

```bash
git clone https://github.com/your-username/assessor-ai.git
cd assessor-ai
```

Install the required Python dependencies:

```bash
pip install fastapi uvicorn pydantic pymongo qdrant-client langchain langchain-google-genai langchain-groq langchain-community pypdf faiss-cpu psycopg2-binary python-dotenv
```

---

### 2. Environment Configuration

Create a `.env` file in the root directory:

```ini
# Core API Keys
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Databases
MONGODB_URI=mongodb://localhost:27017
DATABASE_URL=postgres://user:password@localhost:5432/dbname

# Qdrant Vector Database (Optional for Qdrant Cloud; defaults to local storage if omitted)
QDRANT_URL=https://your-cluster.qdrant.tech
QDRANT_API_KEY=your_qdrant_api_key_here
```

---

### 3. FAQ Vector Ingestion

Before starting the server, ingest the FAQ PDF into Qdrant vector database (run once):

```bash
python -m app.ingest_faq
```

*Expected Output:*
```text
[ingest] Carregando PDF: .../data/FAQ_assessor_v1.1.pdf
[ingest] 3 página(s) carregada(s)
[ingest] 15 chunk(s) gerado(s)
[ingest] Concluído! 15 chunk(s) indexado(s) no Qdrant.
```

---

### 4. Running the Application

Launch the FastAPI web server using Uvicorn:

```bash
uvicorn app.main:app --reload --port 8000
```

The application will start at `http://localhost:8000`.

---

## 🌐 Web Interface & API Documentation

- **Chat Web Console:** Open [`http://localhost:8000/index.html`](http://localhost:8000/index.html) in your browser.
- **User Profile Page:** Open [`http://localhost:8000/perfil.html`](http://localhost:8000/perfil.html) to configure financial goals, monthly income, risk tolerance, and investment preferences.
- **Interactive API Docs (Swagger):** Visit [`http://localhost:8000/docs`](http://localhost:8000/docs) to explore OpenAPI endpoints.

---

## 🔌 API Endpoints Summary

### `POST /chat`
Sends a message to the AI Assessor and returns the orchestrator's response along with the executed agent trail.

**Request Payload:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "usuario_teste",
  "pergunta": "Quanto posso guardar por mês segundo meu perfil?"
}
```

---

### `POST /perfil`
Saves or updates the user's financial profile in MongoDB and Qdrant.

**Request Payload:**
```json
{
  "user_id": "usuario_teste",
  "renda_mensal": 4200.00,
  "objetivo": "juntar para viagem em dezembro",
  "tolerancia_risco": "baixa",
  "preferencias": "quero juntar para uma viagem a João Pessoa em dezembro; não quero investimento agressivo."
}
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
