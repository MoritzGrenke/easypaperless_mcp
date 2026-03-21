"""Credential resolution and SyncPaperlessClient factory for easypaperless-mcp.

Credentials are always provided by the MCP client, never stored server-side:

- **stdio transport** (e.g. Claude Desktop): the MCP client spawns the server
  process and injects ``PAPERLESS_URL`` and ``PAPERLESS_TOKEN`` as process
  environment variables via the ``"env"`` key in ``claude_desktop_config.json``.

- **HTTP transport** (e.g. Docker + mcp-remote): the MCP client passes the
  token via the ``Authorization: Bearer <token>`` header (preferred) or the
  deprecated ``X-Paperless-Token`` header.
  ``PAPERLESS_URL`` may optionally be locked on the server side (Docker env);
  if not set server-side, the client supplies it via the ``X-Paperless-URL``
  header.

The module-level :data:`SERVER_URL` is read from the process environment at
import time.  For HTTP deployments this is the operator-supplied URL that
takes precedence over any client-supplied value.  For stdio deployments it is
whatever the MCP client injected into the process environment — also correct.

:func:`get_client` is called by every tool function.  It reads credentials
from :data:`_request_token` and :data:`_request_url` ContextVars that are set
by :class:`~easypaperless_mcp.server.CredentialMiddleware` before each tool
call.  Unit tests mock :func:`get_client` directly and are unaffected by this
mechanism.
"""

import os
from contextvars import ContextVar

from easypaperless import SyncPaperlessClient

# Server-side URL lock: if the operator sets PAPERLESS_URL in the server
# environment (e.g. Docker), it is used for every client and cannot be
# overridden.  Leave it unset to let each client supply their own URL.
SERVER_URL: str | None = os.environ.get("PAPERLESS_URL") or None

# Per-request ContextVars — set by CredentialMiddleware before each tool call.
_request_token: ContextVar[str | None] = ContextVar("_request_token", default=None)
_request_url: ContextVar[str | None] = ContextVar("_request_url", default=None)


def get_client() -> SyncPaperlessClient:
    """Return a :class:`~easypaperless.SyncPaperlessClient` for the current request.

    Credentials are read from the request-scoped ContextVars populated by
    :class:`~easypaperless_mcp.server.CredentialMiddleware`.

    Returns:
        A :class:`~easypaperless.SyncPaperlessClient` configured with the
        credentials supplied by the current MCP client.

    Raises:
        RuntimeError: If the token or URL is missing from the current request
            context.  The error message guides the operator to configure the
            MCP client, not the server.
    """
    token = _request_token.get()
    url = _request_url.get()

    if not token:
        raise RuntimeError(
            "PAPERLESS_TOKEN is missing. Configure it in your MCP client — do NOT set it on the server.\n"
            "  • stdio / Claude Desktop: add PAPERLESS_TOKEN to the 'env' section of claude_desktop_config.json\n"
            "  • HTTP / mcp-remote: pass --header 'Authorization: Bearer <your-token>'\n"
            "    (legacy alternative: --header 'X-Paperless-Token: <your-token>')"
        )
    if not url:
        raise RuntimeError(
            "PAPERLESS_URL is missing. Configure it in your MCP client.\n"
            "  • stdio / Claude Desktop: add PAPERLESS_URL to the 'env' section of claude_desktop_config.json\n"
            "  • HTTP / mcp-remote: pass --header 'X-Paperless-URL: <your-url>'\n"
            "    (or set PAPERLESS_URL in the server environment to lock it for all clients)"
        )

    return SyncPaperlessClient(url=url, api_token=token)
