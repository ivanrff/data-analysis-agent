from langchain.tools import tool

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv

import duckdb

load_dotenv()

table_name_db = "tabela_vendas"

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
    Busca em documentos TEXTUAIS não estruturados da BimBam Buy.
    
    USE APENAS PARA: Políticas da empresa, regras de negócio, termos de garantia,
    métodos de pagamento aceitos e guias de suporte ao cliente.
    
    NÃO USE PARA: Cálculos numéricos, contagem de vendas ou relatórios de estoque.

    Argumentos:
        consulta: consulta em linguagem natural.

    Retorna:
        Texto formatado com os trechos encontrados.
    """
    retrieved_docs = vector_store.similarity_search(consulta, k=2)
    
    # Dica: converta os documentos em texto formatado para o LLM entender melhor
    formatted_docs = "\n\n".join([doc.page_content for doc in retrieved_docs])
    return formatted_docs

# 1. Caminho para os seus dados (pode ser .csv, .parquet ou .db)
DATA_PATH = "app/data/sales/sales.csv"

def executar_query_duckdb(query: str) -> str:
    """Função auxiliar que executa a query em uma conexão isolada e segura."""
    # Conexão em memória (ou apontando para arquivo) 
    con = duckdb.connect(database=":memory:", read_only=False)
    
    try:
        # Registra o CSV/Parquet como uma visão de leitura no DuckDB
        # (Você também pode carregar arquivos parquet diretamente: 'app/data/*.parquet')
        con.execute(f"CREATE VIEW {table_name_db} AS SELECT * FROM read_csv_auto('{DATA_PATH}')")
        
        # Executa a query gerada pelo LLM
        result = con.execute(query).fetchdf()
        
        # Limita o retorno visual para evitar estourar o limite de tokens da API
        if len(result) > 50:
            return f"{result.head(50).to_string()}\n\n... (Exibindo 50 de {len(result)} linhas)"
        
        return result.to_string() if not result.empty else "Consulta retornou 0 resultados."
        
    except Exception as e:
        return f"Erro ao executar SQL no DuckDB: {str(e)}"
    finally:
        con.close()

def get_db_schema() -> str:
    con = duckdb.connect(database=":memory:")
    # Carrega a visualização da tabela
    con.execute(f"CREATE VIEW {table_name_db} AS SELECT * FROM read_csv_auto('{DATA_PATH}')")
    
    # Executa o DESCRIBE do DuckDB para pegar colunas e tipos automaticamente
    schema_df = con.execute(f"DESCRIBE {table_name_db}").fetchdf()
    con.close()
    
    # Formata como texto simples
    schema_text = ""
    for _, row in schema_df.iterrows():
        schema_text += f"- {row['column_name']} ({row['column_type']})\n"
    return schema_text

@tool(description=f"""
    Executa consultas SQL no DuckDB para obter MÉTRICAS E DADOS NUMÉRICOS ESTRUTURADOS.
    
    USE APENAS PARA: Perguntas analíticas que envolvem números, contagens, 
    somas de vendas, ranking de produtos, médias ou histórico de transações.
    
    NÃO USE PARA: Perguntas sobre regras, termos de uso ou políticas textuais.
    
    Tabela disponível: `{table_name_db}`
    Colunas:
    {get_db_schema()}
    
    Argumentos:
        query_sql: Instrução SQL SELECT válida para DuckDB.
    """)
def consultar_vendas_sql(query_sql: str) -> str:
    "Static docstring for the code, Langchain will use the description above."
    # Trava de segurança no nível do código: aceita APENAS comandos de leitura (SELECT e WITH)
    query_limpa = query_sql.strip().upper()
    if not (query_limpa.startswith("SELECT") or query_limpa.startswith("WITH")):
        return "Erro de Segurança: Apenas consultas de leitura (SELECT / WITH) são permitidas."
    
    return executar_query_duckdb(query_sql)

tools = [buscar_docs, consultar_vendas_sql]

if __name__ == "__main__":
    print(consultar_vendas_sql(f"SELECT * FROM {table_name_db}"))