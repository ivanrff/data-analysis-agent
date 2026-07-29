import duckdb
import pandas as pd
from datetime import datetime

table_name_db = "tabela_vendas"

def clean_csv(csv_path) -> bool:
    data = pd.read_csv(csv_path, index_col="Row ID", sep=";", encoding_errors='replace')

    data.columns = [col_name.replace(" ", "_").lower() for col_name in data.columns.to_list()]

    for col in ["order_date", "ship_date"]:
        data[col] = pd.to_datetime(data[col].str.strip(), format="%d/%m/%Y")

    # time it takes since order to ship
    data["ship_duration"] = data["ship_date"] - data["order_date"]

    # pivoting order dates to 2026
    data["order_date"] = data["order_date"].apply(lambda x: f"{x.strftime(format="%d/%m/%Y")[:-2]}26")
    data["order_date"] = pd.to_datetime(data["order_date"].str.strip(), format="%d/%m/%Y")

    # pivoting ship dates to 2026 by adding ship duration to pivoted order dates
    data["ship_date"] = data['order_date'] + data["ship_duration"]

    # removing orders made in dates in the future after pivoting every date to 2026
    data = data[data['ship_date'] <= datetime.now()].copy()

    data["sales"] = pd.to_numeric(data["sales"].str.strip().str.replace("$", "").str.replace(",", ""))

    data = data.sort_values(by=["ship_date"])
    data = data.drop(columns=["month_&_year_order"])

    data.to_parquet("app/data/sales/sales.parquet", index=None)

    return True
    

# 1. Caminho para os seus dados (pode ser .csv, .parquet ou .db)
DATA_PATH = "app/data/sales/sales.parquet"

_con = None

def init_db():
    global _con
    _con = duckdb.connect(database=":memory:", read_only=False)
    _con.execute(f"CREATE VIEW {table_name_db} AS SELECT * FROM read_parquet('{DATA_PATH}')")

def _get_con():
    if _con is None:
        init_db()
    return _con

def executar_query_duckdb(query: str) -> str:
    """Função auxiliar que executa a query em uma conexão isolada e segura."""
    _get_con()

    try:
        # Executa a query gerada pelo LLM
        result = _con.execute(query).fetchdf()
        
        # Limita o retorno visual para evitar estourar o limite de tokens da API
        if len(result) > 50:
            return f"{result.head(50).to_string()}\n\n... (Exibindo 50 de {len(result)} linhas)"
        
        return result.to_string() if not result.empty else "Consulta retornou 0 resultados."
        
    except Exception as e:
        return f"Erro ao executar SQL no DuckDB: {str(e)}"

def get_db_schema() -> str:

    _get_con()

    # Executa o DESCRIBE do DuckDB para pegar colunas e tipos automaticamente
    schema_df = _con.execute(f"DESCRIBE {table_name_db}").fetchdf()
    
    # Formata como texto simples
    schema_text = ""
    for _, row in schema_df.iterrows():
        schema_text += f"- {row['column_name']} ({row['column_type']})\n"
    return schema_text

# init_db()

if __name__ == "__main__":
    clean_csv("app/data/sales/sales.csv")