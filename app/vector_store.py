from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

# --- EXECUÇÃO ---

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

vector_store = Chroma(
    collection_name="base_conhecimento",
    embedding_function=embeddings,
    persist_directory="app/rag/vectorstore/chroma",
)