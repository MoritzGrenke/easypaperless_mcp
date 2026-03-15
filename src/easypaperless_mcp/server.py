import os

from fastmcp import FastMCP

from .tools.correspondents import correspondents
from .tools.custom_fields import custom_fields
from .tools.document_notes import document_notes
from .tools.document_types import document_types
from .tools.documents import documents
from .tools.storage_paths import storage_paths
from .tools.tags import tags

mcp = FastMCP("easypaperless")
mcp.mount(documents)
mcp.mount(document_notes)
mcp.mount(tags)
mcp.mount(correspondents)
mcp.mount(custom_fields)
mcp.mount(document_types)
mcp.mount(storage_paths)


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
