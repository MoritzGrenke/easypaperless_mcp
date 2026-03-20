import os

import mcp.types as mt
from fastmcp import FastMCP
from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from fastmcp.tools.tool import ToolResult

from .client import SERVER_URL, _request_token, _request_url
from .tools.correspondents import correspondents
from .tools.custom_fields import custom_fields
from .tools.document_notes import document_notes
from .tools.document_types import document_types
from .tools.documents import documents
from .tools.storage_paths import storage_paths
from .tools.tags import tags
from .tools.users import users


class CredentialMiddleware(Middleware):
    """Resolve MCP-client-supplied credentials before each tool call.

    For **stdio** transport the MCP client spawns the server process and
    injects credentials as process environment variables.  Both
    ``PAPERLESS_URL`` and ``PAPERLESS_TOKEN`` are read from ``os.environ``.

    For **HTTP** transport credentials must be passed as HTTP request headers:

    - ``X-Paperless-Token`` — the paperless-ngx API token (required).
    - ``X-Paperless-URL`` — the paperless-ngx base URL (required when
      ``PAPERLESS_URL`` is not set in the server environment).

    If ``PAPERLESS_URL`` **is** set in the server environment, it is used
    regardless of any client-supplied ``X-Paperless-URL`` value.  This lets
    operators lock the target instance in Docker deployments.

    ``PAPERLESS_TOKEN`` is **never** read from the server environment.
    """

    async def on_call_tool(
        self,
        context: MiddlewareContext[mt.CallToolRequestParams],
        call_next: CallNext[mt.CallToolRequestParams, ToolResult],
    ) -> ToolResult:
        from fastmcp.server.context import _current_transport

        transport = _current_transport.get()

        if transport == "stdio":
            token: str | None = os.environ.get("PAPERLESS_TOKEN")
            url: str | None = os.environ.get("PAPERLESS_URL")
        else:
            from fastmcp.server.dependencies import get_http_request

            request = get_http_request()
            token = request.headers.get("x-paperless-token")
            url = SERVER_URL or request.headers.get("x-paperless-url")

        tok = _request_token.set(token)
        url_tok = _request_url.set(url)
        try:
            return await call_next(context)
        finally:
            _request_token.reset(tok)
            _request_url.reset(url_tok)


mcp = FastMCP("easypaperless", middleware=[CredentialMiddleware()])
mcp.mount(documents)
mcp.mount(document_notes)
mcp.mount(tags)
mcp.mount(correspondents)
mcp.mount(custom_fields)
mcp.mount(document_types)
mcp.mount(storage_paths)
mcp.mount(users)


def main() -> None:
    """Start the easypaperless MCP server.

    Reads ``MCP_TRANSPORT`` from the environment to select the transport:

    - ``stdio`` (default) — for local use with Claude Desktop or the MCP
      Inspector.
    - ``streamable-http`` or ``http`` — starts an HTTP server on
      ``0.0.0.0:8000``, intended for Docker / remote deployments.

    Raises:
        ValueError: If ``MCP_TRANSPORT`` is set to an unsupported value.
    """
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport in ("streamable-http", "http"):
        mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
    else:
        raise ValueError(f"Unsupported MCP_TRANSPORT: {transport!r}")


if __name__ == "__main__":
    main()
