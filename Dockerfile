FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Copia só os arquivos de dependência primeiro (cache de camadas)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# Copia o resto do código (graças ao .dockerignore, sem cache/vectorstore/parquet)
COPY . .
RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"

# Script que gera os dados na inicialização, caso não existam
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]