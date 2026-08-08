import duckdb
import pandas as pd
from datetime import datetime
from pathlib import Path
import numpy as np

CSV_PATH = "app/data/sales/sales.csv"
DB_PATH = "app/data/sales/sales.duckdb"
TABLE_NAME = "tabela_vendas"

def create_ingest_db(csv_path) -> bool:
    # making sure the path exists
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

    data = pd.read_csv(csv_path, index_col="Row ID", sep=";", encoding_errors='replace')

    # standardizing column names
    data.columns = [col_name.replace(" ", "_").lower() for col_name in data.columns.to_list()]

    # making dates as date type
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

    # making the sales values more interesting to visualize
    data["sales"] = data["sales"] + np.around(np.random.uniform(low=0.01, high=0.99, size=len(data)), 2)

    # renaming "sales" column to "value" so the LLM understands better what it is
    data.columns = ["value" if col == "sales" else col for col in data.columns]

    # dropping this column that formats the month as a string using month names
    data = data.drop(columns=["month_&_year_order"])

    data = data.sort_values(by=["ship_date"])

    ingest_con = duckdb.connect(DB_PATH)
    ingest_con.sql(f"CREATE OR REPLACE TABLE {TABLE_NAME} AS SELECT * FROM data")
    ingest_con.close()

    return True

def executar_query_duckdb(query: str) -> str:
    """Função auxiliar que executa a query em uma conexão isolada e segura."""

    try:
        with duckdb.connect(DB_PATH, read_only=True, config={"enable_external_access": False}) as con:
            result = con.execute(query).fetchdf()
            
            # Limita o retorno visual para evitar estourar o limite de tokens da API
            if len(result) > 50:
                return f"{result.head(50).to_string()}\n\n... (Exibindo 50 de {len(result)} linhas)"
            
            return result.to_string() if not result.empty else "Consulta retornou 0 resultados."
        
    except Exception as e:
        return f"Erro ao executar SQL no DuckDB: {str(e)}"

def get_db_schema() -> str:

    con = duckdb.connect(DB_PATH, read_only=True, config={"enable_external_access": False})

    # Executa o DESCRIBE do DuckDB para pegar colunas e tipos automaticamente
    schema_df = con.execute(f"DESCRIBE {TABLE_NAME}").fetchdf()
    con.close()
    
    # Formata como texto simples
    schema_text = ""
    for _, row in schema_df.iterrows():
        schema_text += f"- {row['column_name']} ({row['column_type']})\n"
    return schema_text

if __name__ == "__main__":
    create_ingest_db(CSV_PATH)
    print(executar_query_duckdb(f"SELECT * FROM {TABLE_NAME} LIMIT 5"))
    print(get_db_schema())