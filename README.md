# BimBam Buy - Data Analysis Agent

An intelligent virtual assistant developed to help internal employees at **BimBam Buy**. This project uses **LLMs (Large Language Models)** to answer textual questions based on corporate documents (such as policies and manuals) via **RAG (Retrieval-Augmented Generation)**, and performs analytical queries on data and metrics through **Text-to-SQL** in a high-performance database.

## Features

- **Intelligent Context Routing:** The agent dynamically decides whether to query the textual document base (e.g., warranty rules, payment methods) or the structured database (e.g., sales metrics, daily revenue).
- **Secure SQL Queries (DuckDB):** Converts the user's natural language intent into secure queries (only `SELECT` and `WITH` read commands) that are executed on `.parquet` files.
- **RAG with ChromaDB:** Processing, chunking, and vectorization of PDF documents for semantic search using Cohere embeddings.
- **Dynamic Data Visualization:** When requested, the agent generates chart configurations rendered natively and interactively in the frontend using **Plotly.js**.
- **Integrated Web Interface:** Responsive and modern chat with support for Markdown rendering, syntax highlighting for code blocks, and real-time response streaming.

## Technologies Used

- **Backend & AI:** [Python 3.12](https://www.python.org/), [FastAPI](https://fastapi.tiangolo.com/), [LangChain](https://www.langchain.com/), ChatGroq (Llama-3.3-70b-versatile)
- **Data & Databases:** [DuckDB](https://duckdb.org/), [Pandas](https://pandas.pydata.org/), [ChromaDB](https://www.trychroma.com/) (Vector Store)
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla), [Plotly.js](https://plotly.com/javascript/), [Marked.js](https://marked.js.org/)
- **Infrastructure:** [Docker](https://www.docker.com/), [uv](https://github.com/astral-sh/uv) (Ultra-fast package manager)

## Project Structure

```text
app/
 ├── data/
 │   ├── docs/          # PDFs with rules and manuals (e.g., warranty-manual.pdf)
 │   └── sales/         # Sales database directory (Parquet/CSV)
 ├── rag/
 │   └── vectorstore/   # Automatically generated persistent vector database (Chroma)
 ├── static/            # Frontend static files (HTML, CSS, JS, logo)
 ├── tools/
 │   └── tools.py       # LangChain tools definition (search_docs, query_sales_sql)
 ├── agent.py           # Main agent configuration, system prompt, and session memory
 ├── ingest_sales.py    # ETL script for data cleaning and conversion (CSV to Parquet)
 ├── main.py            # FastAPI API entrypoint and chat endpoints
 └── vector_store.py    # PDF processing and chunk synchronization with ChromaDB
```

## Setup and Execution

### Prerequisites

- **Docker** and **Docker Compose** installed (Recommended).
- A **Groq** API Key (`GROQ_API_KEY`).
- A **Cohere** API Key (`COHERE_API_KEY`) for embedding generation.

### 1. Environment Variables

Create a `.env` file in the root of the project containing the necessary credentials:

```ini
GROQ_API_KEY=your_groq_api_key_here
COHERE_API_KEY=your_cohere_api_key_here
```

### 2. Running with Docker (Recommended)

The project includes a `docker-compose.yml` and an `entrypoint.sh` script configured to process and structure the data and initialize the application automatically.

At the root of the repository, run:
```bash
docker-compose up --build
```
The interactive web application will be immediately available at: `http://localhost:8000`

### 3. Running Locally (Development Mode)

If you prefer to run without Docker, using the `uv` package manager:

```bash
# Sync and install all dependencies from pyproject.toml
uv sync

# Activate the created virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Optional: Generate the base data and embeddings manually (if it's the first run)
python -m app.ingest_sales
python -m app.vector_store

# Start the ASGI FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## How the Agent Works (Core)

The system orchestrator is defined in the `agent.py` file. Based on the user's intent:
1. **Operational/Textual Questions:** Trigger the `buscar_docs` tool, which performs a semantic similarity search (Top-K) in the ChromaDB base to bring context to the response.
2. **Analytical Questions:** Trigger the `consultar_vendas_sql` tool, which autonomously generates a query supported by DuckDB, queries the highly efficient `.parquet` file, and consolidates the numerical data.
3. **Graphical Representation:** If the user requests a chart in the response, the LLM is instructed by its System Prompt to return a special `json-chart` Markdown code block. The JavaScript in `chat.js` intercepts this block and creates an interactive chart using the Plotly library without requiring extra server processing.
