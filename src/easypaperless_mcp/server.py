import logging
import os
from collections.abc import Sequence
from typing import cast

import mcp.types as mt
from fastmcp import FastMCP
from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from fastmcp.tools import Tool, ToolResult

from .client import SERVER_URL, _request_token, _request_url
from .permissions import filter_tools_by_permissions, get_effective_permissions
from .tools.correspondents import correspondents
from .tools.custom_fields import custom_fields
from .tools.document_history import document_history
from .tools.document_notes import document_notes
from .tools.document_types import document_types
from .tools.documents import documents
from .tools.storage_paths import storage_paths
from .tools.tags import tags
from .tools.trash import trash
from .tools.users import users

logger = logging.getLogger(__name__)

# Session-state key used to cache resolved permissions across list_tools calls.
_SESSION_PERM_KEY = "_perm_resolved"


class CredentialMiddleware(Middleware):
    """Resolve MCP-client-supplied credentials before each tool call.

    For **stdio** transport the MCP client spawns the server process and
    injects credentials as process environment variables.  Both
    ``PAPERLESS_URL`` and ``PAPERLESS_TOKEN`` are read from ``os.environ``.

    For **HTTP** transport credentials must be passed as HTTP request headers:

    - ``Authorization: Bearer <token>`` — the paperless-ngx API token
      (preferred).
    - ``X-Paperless-Token`` — the paperless-ngx API token (deprecated;
      a warning is logged when used).  If both headers are present,
      ``Authorization: Bearer`` takes precedence.
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
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[len("Bearer ") :]
            else:
                x_token = request.headers.get("x-paperless-token")
                if x_token:
                    logger.warning(
                        "X-Paperless-Token is deprecated. "
                        "Use 'Authorization: Bearer <token>' instead."
                    )
                token = x_token
            url = SERVER_URL or request.headers.get("x-paperless-url")

        tok = _request_token.set(token)
        url_tok = _request_url.set(url)
        try:
            return await call_next(context)
        finally:
            _request_token.reset(tok)
            _request_url.reset(url_tok)


class PermissionMiddleware(Middleware):
    """Filter the tool list based on the authenticated user's Django permissions.

    When ``PAPERLESS_USERNAME`` (stdio) or ``X-Paperless-Username`` (HTTP) is
    supplied, the server resolves that user's effective permissions on the first
    ``list_tools`` request and hides tools the user is not permitted to invoke.
    Subsequent ``list_tools`` requests in the same session use the cached result
    without making another API call.

    If no username is supplied, all tools are shown and permission enforcement
    falls back to paperless-ngx's own 403 responses.

    This is a **convenience / UX feature**, not a security boundary.
    """

    async def on_list_tools(
        self,
        context: MiddlewareContext[mt.ListToolsRequest],
        call_next: CallNext[mt.ListToolsRequest, Sequence[Tool]],
    ) -> Sequence[Tool]:
        tools = list(await call_next(context))

        ctx = context.fastmcp_context
        if ctx is None:
            return tools

        # Return cached result if permissions were already resolved this session.
        try:
            cached: dict[str, object] | None = await ctx.get_state(_SESSION_PERM_KEY)
        except Exception:
            return tools

        if cached is not None:
            if cached["show_all"]:
                return tools
            return filter_tools_by_permissions(tools, set(cast(list[str], cached["perms"])))

        # First list_tools for this session — resolve permissions.
        from fastmcp.server.context import _current_transport

        transport = _current_transport.get()

        username: str | None
        token: str | None
        url: str | None

        if transport == "stdio":
            username = os.environ.get("PAPERLESS_USERNAME")
            token = os.environ.get("PAPERLESS_TOKEN")
            url = os.environ.get("PAPERLESS_URL")
        else:
            from fastmcp.server.dependencies import get_http_request

            request = get_http_request()
            username = request.headers.get("x-paperless-username")
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[len("Bearer ") :]
            else:
                token = request.headers.get("x-paperless-token")
            url = SERVER_URL or request.headers.get("x-paperless-url")

        if not username:
            await ctx.set_state(_SESSION_PERM_KEY, {"show_all": True, "perms": []})
            return tools

        if not token or not url:
            raise RuntimeError(
                f"Cannot resolve permissions for user {username!r}: "
                "PAPERLESS_TOKEN or PAPERLESS_URL is missing."
            )

        from easypaperless.client import PaperlessClient

        try:
            async with PaperlessClient(url=url, api_token=token) as client:
                result = await client.users.list(username_exact=username)
        except Exception as exc:
            raise RuntimeError(f"Permission lookup failed for user {username!r}: {exc}") from exc

        if not result.results:
            raise RuntimeError(
                f"Permission lookup failed: user {username!r} not found in paperless-ngx."
            )

        user = result.results[0]

        if user.is_superuser:
            await ctx.set_state(_SESSION_PERM_KEY, {"show_all": True, "perms": []})
            return tools

        effective_perms = get_effective_permissions(user)
        await ctx.set_state(
            _SESSION_PERM_KEY,
            {"show_all": False, "perms": list(effective_perms)},
        )
        return filter_tools_by_permissions(tools, effective_perms)


mcp = FastMCP("easypaperless", middleware=[CredentialMiddleware(), PermissionMiddleware()])
mcp.mount(documents)
mcp.mount(document_history)
mcp.mount(document_notes)
mcp.mount(tags)
mcp.mount(correspondents)
mcp.mount(custom_fields)
mcp.mount(document_types)
mcp.mount(storage_paths)
mcp.mount(trash)
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
