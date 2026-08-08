from langchain.tools import tool

from dotenv import load_dotenv

from app.vector_store import vector_store

from app.ingest_sales import get_db_schema, TABLE_NAME, executar_query_duckdb

load_dotenv()

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

@tool(description=f"""
    Executa consultas SQL no DuckDB para obter MÉTRICAS E DADOS NUMÉRICOS ESTRUTURADOS.
    
    USE APENAS PARA: Perguntas analíticas que envolvem números, contagens, 
    somas de vendas, ranking de produtos, médias ou histórico de transações.
    
    NÃO USE PARA: Perguntas sobre regras, termos de uso ou políticas textuais.
    
    Tabela disponível: `{TABLE_NAME}`
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