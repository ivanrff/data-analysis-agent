from langchain.tools import tool

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

vector_store = Chroma(
    collection_name="base_conhecimento",
    embedding_function=embeddings,
    persist_directory="app/rag/vectorstore/chroma",
)

@tool
def buscar_docs(consulta: str) -> str:
    """
    Busca nas documentações da empresa e retorna os resultados.

    Argumentos:
        consulta: consulta em linguagem natural.

    Retorna:
        Texto formatado com os trechos encontrados.
    """
    retrieved_docs = vector_store.similarity_search(consulta, k=2)
    
    # Dica: converta os documentos em texto formatado para o LLM entender melhor
    formatted_docs = "\n\n".join([doc.page_content for doc in retrieved_docs])
    return formatted_docs

tools = [buscar_docs]