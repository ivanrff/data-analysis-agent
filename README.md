# Data Analysis Agent

An intelligent virtual assistant developed to help internal employees at a ficticial e-commerce called **BimBam Buy**. This project uses **LLMs (Large Language Models)** to answer textual questions based on corporate documents (such as policies and manuals) via **RAG (Retrieval-Augmented Generation)**, and performs analytical queries on data and metrics through **Text-to-SQL** in a high-performance database.

**Deployment Note:** This project was deployed on Oracle and can be accessed [here](http://163.176.57.167:8000/).

## Table of Contents
- [Key Features](#key-features)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Setup and Execution](#setup-and-execution)
  - [Prerequisites](#prerequisites)
  - [1. Environment Variables](#1-environment-variables)
  - [2. Running with Docker (Recommended)](#2-running-with-docker-recommended)
  - [3. Running Locally (Development Mode)](#3-running-locally-development-mode)
- [How the Agent Works (Core)](#how-the-agent-works-core)
- [Some Design Choices](#some-design-choices)

## Key Features
- **Dual-Engine Querying:** 
  - **RAG (Retrieval-Augmented Generation):** Searches unstructured textual documents (e.g., PDFs for warranties, payment methods) using ChromaDB and Cohere embeddings.
  - **SQL Agent:** Executes read-only queries against a DuckDB database containing sales data to answer numerical and analytical questions.
- **Interactive Web Interface:** A lightweight frontend built with HTML/JS/CSS that supports Markdown rendering, code highlighting, and dynamic charting using Plotly.
- **Conversational Memory:** Retains full message history within the same session, enabling multi-turn context awareness and natural follow-up queries.
- **Streaming Responses:** Provides real-time streaming output using FastAPI and LangGraph.
- **Intelligent Routing:** The Groq-powered LangChain agent (using the Qwen model) automatically decides which tool to use based on the user's natural language input.
- **Rate Limiting:** Built-in rate limiting using `slowapi` to prevent API abuse.

## Technologies Used

- **Backend & AI:** [Python 3.12](https://www.python.org/), [FastAPI](https://fastapi.tiangolo.com/), [LangChain](https://www.langchain.com/), ChatGroq (currently `qwen/qwen3.6-27b`);
- **Data & Databases:** [DuckDB](https://duckdb.org/) for the sales data, [ChromaDB](https://www.trychroma.com/) for the embeddings vector store;
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla), [Plotly.js](https://plotly.com/javascript/), [Marked.js](https://marked.js.org/) for markdown formatting of the LLM's output;
- **Infrastructure:** [Docker](https://www.docker.com/) for deploying on Oracle Cloud, [uv](https://github.com/astral-sh/uv) for managing Python dependencies;

## Project Structure

```text
app/
 ├── data/
 │   ├── docs/          # PDFs with organizational rules and manuals
 │   └── sales/         # Sales database directory (CSV → DuckDB)
 ├── rag/
 │   └── vectorstore/   # Automatically generated persistent vector database (Chroma)
 ├── static/            # Frontend static files (HTML, CSS, JS, logo)
 ├── tools/
 │   └── tools.py       # LangChain tools definition (search_docs, query_sales_sql)
 ├── agent.py           # Main agent configuration, system prompt, and session memory
 ├── ingest_sales.py    # ETL script for data cleaning and conversion (CSV to DuckDB)
 ├── main.py            # FastAPI API entrypoint and chat endpoints
 └── vector_store.py    # PDF processing and chunk synchronization with ChromaDB
```

## Setup and Execution

### Prerequisites

- **Docker** and **Docker Compose** installed (Recommended).
- A **Groq** API Key (`GROQ_API_KEY`).
- A **Cohere** API Key (`COHERE_API_KEY`) for embedding generation.

### 1. Environment Variables

Copy the `.env.example` file to `.env` and fill in your API keys:
```bash
cp .env.example .env
```
Required keys:
- `GROQ_API_KEY`
- `COHERE_API_KEY`

### 2. Running with Docker (Recommended)

The project includes a `docker-compose.yml` and an `entrypoint.sh` script configured to process and structure the data and initialize the application automatically.

At the root of the repository, run:
```bash
docker-compose up --build
```

After the docker image is built, the `entrypoint.sh` will automatically call:
- `ingest_sales.py`, which will use `sales.csv` to ingest sales data into `sales.duckdb`;
- `vector_store.py`, which will use the pdfs from `app/data/docs/` to generate a `ChromaDB` vector store in `app/rag/vectorstore`;

The interactive web application will be immediately available at: `http://localhost:8000`

### 3. Running Locally (Development Mode)

If you prefer to run without Docker, using the `uv` package manager:

```bash
# Sync and install all dependencies from pyproject.toml
uv sync

# Optional: Generate the base data and embeddings manually (if it's the first run)
uv run python -m app.ingest_sales
uv run python -m app.vector_store

# Start the FastAPI server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## How the Agent Works (Core)

The system orchestrator is defined in the `agent.py` file. Based on the user's intent:
1. **Operational/Textual Questions:** Trigger the `buscar_docs` tool, which performs a semantic similarity search (Top-K) in the ChromaDB base to bring context to the response.
2. **Analytical Questions:** Trigger the `consultar_vendas_sql` tool, which autonomously generates a query supported by DuckDB, queries the highly efficient `.parquet` file, and consolidates the numerical data.
3. **Graphical Representation:** If the user requests a chart in the response, the LLM is instructed by its System Prompt to return a special `json-chart` Markdown code block. The JavaScript in `chat.js` intercepts this block and creates an interactive chart using the Plotly library without requiring extra server processing.

## Some Design Choices

- **LLM Providers:** `Cohere` and `Groq` were chosen as they provide a free tier API for LLM access.
    - For that reason, the agent is limited both via `max_tokens` and `recursion_limit`.
- **Embeddings:** The text files are split with `RecursiveCharacterTextSplitter` with `(chunk_size=1000, chunk_overlap=200)`. Although this was an arbitrary first test, it managed to return satisfying results. In the future I might look into optimizing it, if my goal is to go deeper into RAG systems.
- **Sales Data:** The source of the sales data is the [Superstore Sales Dataset](https://www.kaggle.com/datasets/ishanshrivastava28/superstore-sales). I took the liberty to make some changes along with the data cleaning inside `ingest_sales.py` to make the interactions more interesting, like appending the dates to be more recent, adding cents to the value column, and other changes to remove confusion during agent interactions.
- **LangChain:** The agent was designed using best practices suggested by the LangChain docs after v1 changes, like using checkpointer for message history and the `create_agent` module.
- **Agent Memory:** In-memory storage that holds a limited amount of thread ids, and with the agent.touch_thread() function I can control the number of threads to mitigate memory leaks over time.
- **Agent Security & Safety:** Database connections to DuckDB are strictly set to `read_only` with host file-system access disabled, preventing unauthorized schema mutations or file access during text-to-SQL execution.