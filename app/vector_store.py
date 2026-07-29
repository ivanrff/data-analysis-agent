
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

import hashlib
import glob
import os
from dotenv import load_dotenv
import pypdf

# Embeddings model
# from langchain_huggingface import HuggingFaceEmbeddings
from langchain_cohere import CohereEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Vector Store Engine
from langchain_chroma import Chroma

load_dotenv()

# embeddings = GoogleGenerativeAIEmbeddings(
#     model="models/gemini-embedding-001",
#     google_api_key=os.getenv("GEMINI_API_KEY")
# )
# embeddings = HuggingFaceEmbeddings(
#     model="sentence-transformers/all-MiniLM-L6-v2"
# )
embeddings = CohereEmbeddings(
    model="embed-multilingual-v3.0"
)

vector_store = Chroma(
    collection_name="base_conhecimento",
    embedding_function=embeddings,
    persist_directory="app/rag/vectorstore/chroma",
)


# 1. Função para carregar e quebrar PDFs
def process_pdf_folder(folder_path: str) -> list[Document]:
    pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
    all_docs = []
    
    for file_path in pdf_files:
        reader = pypdf.PdfReader(file_path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                all_docs.append(
                    Document(
                        page_content=text,
                        metadata={
                            "source": file_path, 
                            "file_name": os.path.basename(file_path),
                            "page": i + 1
                        },
                    )
                )
    return all_docs

# 2. Função para gerar IDs únicos e determinísticos
def generate_deterministic_id(doc: Document) -> str:
    """
    Gera uma string MD5 única baseada no nome do arquivo, página e conteúdo.
    Se o conteúdo do chunk não mudar, o ID gerado será rigorosamente o mesmo.
    """
    raw_identifier = f"{doc.metadata['source']}_{doc.metadata['page']}_{doc.page_content}"
    return hashlib.md5(raw_identifier.encode('utf-8')).hexdigest()

def sync_docs_to_db(docs_directory: str, vector_store):
    # Carrega todos os PDFs da pasta
    raw_docs = process_pdf_folder(docs_directory)
    if not raw_docs:
        print("Nenhum arquivo PDF encontrado na pasta.")
        return

    # Divide em chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(raw_docs)

    # Gerar a lista de IDs determinísticos
    chunk_ids = [generate_deterministic_id(chunk) for chunk in chunks]

    # Buscar quais IDs já existem no Chroma
    existing_records = vector_store.get()
    existing_ids = set(existing_records["ids"]) if existing_records and "ids" in existing_records else set()

    # Identificar apenas os novos chunks
    new_chunks = []
    new_ids = []

    for chunk, chunk_id in zip(chunks, chunk_ids):
        if chunk_id not in existing_ids:
            new_chunks.append(chunk)
            new_ids.append(chunk_id)

    # Adicionar apenas o que é estritamente novo ao banco
    if new_chunks:
        print(f"Adicionando {len(new_chunks)} novos chunks ao Chroma...")
        vector_store.add_documents(documents=new_chunks, ids=new_ids)
        print("Ingestão concluída com sucesso!")
    else:
        print("Todos os documentos já estão atualizados no banco (0 novos chunks).")

if __name__ == "__main__":
    # Pasta contendo os PDFs do seu projeto
    DOCS_DIR = "app/data/docs" 

    sync_docs_to_db(DOCS_DIR, vector_store)