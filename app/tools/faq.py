from langchain.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import GEMINI_API_KEY, FAQ_PDF_PATH


embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview",
    google_api_key=GEMINI_API_KEY
)

PDF_PATH = FAQ_PDF_PATH
loader = PyPDFLoader(PDF_PATH)
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=150)
chunks = splitter.split_documents(docs)

db = FAISS.from_documents(chunks, embeddings)

@tool("faq_retriever")
def search_faq(question: str) -> str:
    """Busca informações no FAQ oficial"""

    results = db.similarity_search(question, k=6)

    if not results:
        return "Nenhuma informação encontrada no FAQ."

    return "\n\n".join(
        result.page_content for result in results
    )