from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# --- EXECUÇÃO ---

embeddings = HuggingFaceEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = Chroma(
    collection_name="base_conhecimento",
    embedding_function=embeddings,
    persist_directory="app/rag/vectorstore/chroma",
)