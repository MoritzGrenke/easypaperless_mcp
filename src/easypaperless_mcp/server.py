import os
from typing import Optional

from fastmcp import FastMCP
from easypaperless import SyncPaperlessClient

mcp = FastMCP("easypaperless")

_client: Optional[SyncPaperlessClient] = None


def get_client() -> SyncPaperlessClient:
    global _client
    if _client is None:
        url = os.environ.get("PAPERLESS_URL")
        token = os.environ.get("PAPERLESS_TOKEN")
        if not url or not token:
            raise RuntimeError(
                "PAPERLESS_URL and PAPERLESS_TOKEN environment variables must be set"
            )
        _client = SyncPaperlessClient(url=url, api_key=token)
    return _client


@mcp.tool
def list_documents(
    search: str = "",
    max_results: int = 25,
    ordering: str = "-added",
) -> list[dict]:
    """List documents from paperless-ngx, optionally filtered by a search query."""
    client = get_client()
    kwargs: dict = {"max_results": max_results, "ordering": ordering}
    if search:
        kwargs["search"] = search
    docs = client.documents.list(**kwargs)
    return [doc.model_dump() for doc in docs]


@mcp.tool
def get_document(document_id: int) -> dict:
    """Retrieve a single document by its ID."""
    client = get_client()
    doc = client.documents.get(id=document_id)
    return doc.model_dump()


@mcp.tool
def search_documents(query: str, max_results: int = 25) -> list[dict]:
    """Full-text search for documents matching the given query string."""
    client = get_client()
    docs = client.documents.list(search=query, max_results=max_results)
    return [doc.model_dump() for doc in docs]


def main() -> None:
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport in ("streamable-http", "http"):
        mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
    else:
        raise ValueError(f"Unsupported MCP_TRANSPORT: {transport!r}")


if __name__ == "__main__":
    main()
