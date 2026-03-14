FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY pyproject.toml .
RUN uv sync --no-dev

COPY src/ src/

ENV MCP_TRANSPORT=streamable-http

EXPOSE 8000

CMD ["uv", "run", "easypaperless-mcp"]
