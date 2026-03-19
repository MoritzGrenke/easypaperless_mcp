FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock .
RUN uv sync --no-dev --frozen

COPY src/ src/

ENV MCP_TRANSPORT=streamable-http

EXPOSE 8000

CMD ["uv", "run", "easypaperless-mcp"]
