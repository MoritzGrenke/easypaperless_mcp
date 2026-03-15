import os

from fastmcp import FastMCP

from .tools.documents import documents
from .tools.tags import tags

mcp = FastMCP("easypaperless")
mcp.mount(documents)
mcp.mount(tags)


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
