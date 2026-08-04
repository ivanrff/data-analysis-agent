# BimBam Buy - Data Analysis Agent

Um assistente virtual inteligente desenvolvido para auxiliar os colaboradores internos da **BimBam Buy**. Este projeto utiliza **LLMs (Large Language Models)** para responder perguntas textuais baseadas em documentos corporativos (como políticas e manuais) via **RAG (Retrieval-Augmented Generation)**, e realiza consultas analíticas de dados e métricas através de **Text-to-SQL** em uma base de alta performance.

## Funcionalidades

- **Roteamento Inteligente de Contexto:** O agente decide dinamicamente se deve consultar a base de documentos textuais (ex: regras de garantia, métodos de pagamento) ou a base de dados estruturada (ex: métricas de vendas, faturamento diário).
- **Consultas SQL Seguras (DuckDB):** Converte a intenção em linguagem natural do usuário em queries seguras (apenas comandos de leitura `SELECT` e `WITH`) que são executadas em arquivos `.parquet`.
- **RAG com ChromaDB:** Processamento, divisão em chunks e vetorização de documentos em PDF para buscas semânticas utilizando embeddings da Cohere.
- **Visualização de Dados Dinâmica:** Quando solicitado, o agente gera configurações de gráficos renderizadas de forma nativa e interativa no frontend utilizando **Plotly.js**.
- **Interface Web Integrada:** Chat responsivo e moderno com suporte a renderização Markdown, highlight de código de sintaxe e streaming em tempo real das respostas.

## Tecnologias Utilizadas

- **Backend & IA:** [Python 3.12](https://www.python.org/), [FastAPI](https://fastapi.tiangolo.com/), [LangChain](https://www.langchain.com/), ChatGroq (Llama-3.3-70b-versatile)
- **Dados & Banco de Dados:** [DuckDB](https://duckdb.org/), [Pandas](https://pandas.pydata.org/), [ChromaDB](https://www.trychroma.com/) (Vector Store)
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla), [Plotly.js](https://plotly.com/javascript/), [Marked.js](https://marked.js.org/)
- **Infraestrutura:** [Docker](https://www.docker.com/), [uv](https://github.com/astral-sh/uv) (Gerenciador de pacotes ultrarrápido)

## Estrutura do Projeto

```text
app/
 ├── data/
 │   ├── docs/          # PDFs com regras e manuais (ex: manuais-garantia.pdf)
 │   └── sales/         # Diretório da base de dados de vendas (Parquet/CSV)
 ├── rag/
 │   └── vectorstore/   # Banco vetorial persistente (Chroma) gerado automaticamente
 ├── static/            # Arquivos estáticos do frontend (HTML, CSS, JS, logo)
 ├── tools/
 │   └── tools.py       # Definição das ferramentas do LangChain (buscar_docs, consultar_vendas_sql)
 ├── agent.py           # Configuração do agente principal, prompt de sistema e memória de sessão
 ├── ingest_sales.py    # Script ETL de limpeza e conversão de dados (CSV para Parquet)
 ├── main.py            # Entrypoint da API FastAPI e endpoints do chat
 └── vector_store.py    # Processamento de PDFs e sincronização de chunks com ChromaDB
```

## Configuração e Execução

### Pré-requisitos

- **Docker** e **Docker Compose** instalados (Recomendado).
- Uma chave de API da **Groq** (`GROQ_API_KEY`).
- Uma chave de API da **Cohere** (`COHERE_API_KEY`) para a geração de embeddings.

### 1. Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto contendo as credenciais necessárias:

```ini
GROQ_API_KEY=sua_chave_groq_aqui
COHERE_API_KEY=sua_chave_cohere_aqui
```

### 2. Rodando com Docker (Recomendado)

O projeto possui um `docker-compose.yml` e um script `entrypoint.sh` configurados para processar e estruturar os dados e inicializar a aplicação automaticamente.

Na raiz do repositório, execute:
```bash
docker-compose up --build
```
A aplicação web interativa estará disponível imediatamente em: `http://localhost:8000`

### 3. Rodando Localmente (Modo de Desenvolvimento)

Caso prefira rodar sem Docker, utilizando o gerenciador de pacotes `uv`:

```bash
# Sincronize e instale todas as dependências do pyproject.toml
uv sync

# Ative o ambiente virtual criado
source .venv/bin/activate  # ou .venv\Scripts\activate no Windows

# Opcional: Gerar os dados base e embeddings manualmente (caso seja a primeira execução)
python -m app.ingest_sales
python -m app.vector_store

# Inicie o servidor ASGI FastAPI
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Como o Agente Funciona (Core)

O orquestrador do sistema é definido no arquivo `agent.py`. Baseado na intenção do usuário:
1. **Dúvidas Operacionais/Textuais:** Disparam a tool `buscar_docs`, que faz uma busca de similaridade semântica (Top-K) na base do ChromaDB para trazer contexto para a resposta.
2. **Dúvidas Analíticas:** Disparam a tool `consultar_vendas_sql`, que gera de forma autônoma uma query suportada pelo DuckDB, consulta o arquivo `.parquet` de alta eficiência e consolida os dados numéricos.
3. **Representação Gráfica:** Se o usuário manifesta o desejo por um gráfico na resposta, o LLM é instruído por seu System Prompt a devolver um bloco de código do tipo `json-chart`. O JavaScript presente em `chat.js` intercepta esse bloco Markdown especial e cria um gráfico interativo através da biblioteca Plotly sem precisar de processamento extra no servidor.