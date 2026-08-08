#!/bin/bash
set -e

if [ ! -f "app/data/sales/sales.duckdb" ]; then
    echo "Gerando sales.duckdb..."
    python -m app.ingest_sales
fi

if [ ! -d "app/rag/vectorstore/chroma" ]; then
    echo "Gerando vector store..."
    python -m app.vector_store
fi

echo "Iniciando aplicação..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000