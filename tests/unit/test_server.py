"""Unit tests for CredentialMiddleware in server.py."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from easypaperless_mcp.server import CredentialMiddleware
from easypaperless_mcp.client import _request_token, _request_url


@pytest.fixture
def middleware():
    return CredentialMiddleware()


@pytest.fixture
def call_next():
    """Async mock for the call_next argument."""
    return AsyncMock(return_value=MagicMock())


@pytest.fixture
def context():
    return MagicMock()


@pytest.fixture(autouse=True)
def reset_contextvars():
    """Reset ContextVars to default (None) around each test."""
    tok = _request_token.set(None)
    url = _request_url.set(None)
    yield
    _request_token.reset(tok)
    _request_url.reset(url)


def _make_transport_mock(transport_name: str):
    """Return a mock for _current_transport with .get() returning transport_name."""
    m = MagicMock()
    m.get.return_value = transport_name
    return m


def _make_http_request(headers: dict[str, str]) -> MagicMock:
    """Return a mock HTTP request whose .headers.get() reads from the given dict."""
    request = MagicMock()
    request.headers.get = lambda key, default=None: headers.get(key, default)
    return request


# ---------------------------------------------------------------------------
# stdio transport
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_stdio_sets_token_from_env(middleware, call_next, context, monkeypatch):
    """stdio transport must read token from PAPERLESS_TOKEN env var."""
    monkeypatch.setenv("PAPERLESS_TOKEN", "env-token")
    monkeypatch.setenv("PAPERLESS_URL", "http://localhost:8000")

    transport_mock = _make_transport_mock("stdio")
    with patch("fastmcp.server.context._current_transport", transport_mock):
        await middleware.on_call_tool(context, call_next)

    assert call_next.called
    # Capture the token that was set during call_next
    captured_token = None

    async def capture(ctx):
        nonlocal captured_token
        captured_token = _request_token.get()
        return MagicMock()

    with patch("fastmcp.server.context._current_transport", transport_mock):
        await middleware.on_call_tool(context, capture)

    assert captured_token == "env-token"


@pytest.mark.asyncio
async def test_stdio_sets_url_from_env(middleware, context, monkeypatch):
    """stdio transport must read URL from PAPERLESS_URL env var."""
    monkeypatch.setenv("PAPERLESS_TOKEN", "env-token")
    monkeypatch.setenv("PAPERLESS_URL", "http://paperless.local:8080")

    captured_url = None

    async def capture(ctx):
        nonlocal captured_url
        captured_url = _request_url.get()
        return MagicMock()

    transport_mock = _make_transport_mock("stdio")
    with patch("fastmcp.server.context._current_transport", transport_mock):
        await middleware.on_call_tool(context, capture)

    assert captured_url == "http://paperless.local:8080"


@pytest.mark.asyncio
async def test_stdio_clears_contextvars_after_call(middleware, call_next, context, monkeypatch):
    """ContextVars must be reset to their prior values after call_next returns."""
    monkeypatch.setenv("PAPERLESS_TOKEN", "env-token")
    monkeypatch.setenv("PAPERLESS_URL", "http://localhost:8000")

    # Set a "prior" value to ensure reset goes back to it, not just None
    prior_tok = _request_token.set("prior-token")
    prior_url = _request_url.set("http://prior-url")

    transport_mock = _make_transport_mock("stdio")
    with patch("fastmcp.server.context._current_transport", transport_mock):
        await middleware.on_call_tool(context, call_next)

    assert _request_token.get() == "prior-token"
    assert _request_url.get() == "http://prior-url"

    _request_token.reset(prior_tok)
    _request_url.reset(prior_url)


# ---------------------------------------------------------------------------
# HTTP transport
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_http_sets_token_from_header(middleware, context):
    """HTTP transport must read token from X-Paperless-Token header."""
    captured_token = None

    async def capture(ctx):
        nonlocal captured_token
        captured_token = _request_token.get()
        return MagicMock()

    request = _make_http_request({"x-paperless-token": "header-token", "x-paperless-url": "http://x"})
    transport_mock = _make_transport_mock("http")

    with patch("fastmcp.server.context._current_transport", transport_mock), \
         patch("fastmcp.server.dependencies.get_http_request", return_value=request), \
         patch("easypaperless_mcp.server.SERVER_URL", None):
        await middleware.on_call_tool(context, capture)

    assert captured_token == "header-token"


@pytest.mark.asyncio
async def test_http_sets_url_from_header_when_server_url_unset(middleware, context):
    """HTTP transport must use X-Paperless-URL header when SERVER_URL is None."""
    captured_url = None

    async def capture(ctx):
        nonlocal captured_url
        captured_url = _request_url.get()
        return MagicMock()

    request = _make_http_request({"x-paperless-token": "tok", "x-paperless-url": "http://client-url"})
    transport_mock = _make_transport_mock("http")

    with patch("fastmcp.server.context._current_transport", transport_mock), \
         patch("fastmcp.server.dependencies.get_http_request", return_value=request), \
         patch("easypaperless_mcp.server.SERVER_URL", None):
        await middleware.on_call_tool(context, capture)

    assert captured_url == "http://client-url"


@pytest.mark.asyncio
async def test_http_server_url_overrides_client_header(middleware, context):
    """SERVER_URL must take precedence over X-Paperless-URL header."""
    captured_url = None

    async def capture(ctx):
        nonlocal captured_url
        captured_url = _request_url.get()
        return MagicMock()

    # Client supplies a different URL in the header
    request = _make_http_request({"x-paperless-token": "tok", "x-paperless-url": "http://client-url"})
    transport_mock = _make_transport_mock("http")

    with patch("fastmcp.server.context._current_transport", transport_mock), \
         patch("fastmcp.server.dependencies.get_http_request", return_value=request), \
         patch("easypaperless_mcp.server.SERVER_URL", "http://server-locked-url"):
        await middleware.on_call_tool(context, capture)

    assert captured_url == "http://server-locked-url"


@pytest.mark.asyncio
async def test_http_no_token_header_sets_none(middleware, context):
    """Missing X-Paperless-Token sets _request_token to None (error surfaces in get_client)."""
    captured_token = "sentinel"

    async def capture(ctx):
        nonlocal captured_token
        captured_token = _request_token.get()
        return MagicMock()

    request = _make_http_request({"x-paperless-url": "http://x"})
    transport_mock = _make_transport_mock("http")

    with patch("fastmcp.server.context._current_transport", transport_mock), \
         patch("fastmcp.server.dependencies.get_http_request", return_value=request), \
         patch("easypaperless_mcp.server.SERVER_URL", None):
        await middleware.on_call_tool(context, capture)

    assert captured_token is None


@pytest.mark.asyncio
async def test_http_no_url_header_and_no_server_url_sets_none(middleware, context):
    """Missing URL in both header and SERVER_URL sets _request_url to None."""
    captured_url = "sentinel"

    async def capture(ctx):
        nonlocal captured_url
        captured_url = _request_url.get()
        return MagicMock()

    request = _make_http_request({"x-paperless-token": "tok"})
    transport_mock = _make_transport_mock("http")

    with patch("fastmcp.server.context._current_transport", transport_mock), \
         patch("fastmcp.server.dependencies.get_http_request", return_value=request), \
         patch("easypaperless_mcp.server.SERVER_URL", None):
        await middleware.on_call_tool(context, capture)

    assert captured_url is None


# ---------------------------------------------------------------------------
# HTTP transport — Authorization: Bearer header
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_http_sets_token_from_authorization_bearer(middleware, context):
    """Authorization: Bearer token must be extracted and used as paperless token."""
    captured_token = None

    async def capture(ctx):
        nonlocal captured_token
        captured_token = _request_token.get()
        return MagicMock()

    request = _make_http_request({"authorization": "Bearer bearer-token", "x-paperless-url": "http://x"})
    transport_mock = _make_transport_mock("http")

    with patch("fastmcp.server.context._current_transport", transport_mock), \
         patch("fastmcp.server.dependencies.get_http_request", return_value=request), \
         patch("easypaperless_mcp.server.SERVER_URL", None):
        await middleware.on_call_tool(context, capture)

    assert captured_token == "bearer-token"


@pytest.mark.asyncio
async def test_http_bearer_takes_precedence_over_x_paperless_token(middleware, context):
    """When both Authorization: Bearer and X-Paperless-Token are present, Bearer wins."""
    captured_token = None

    async def capture(ctx):
        nonlocal captured_token
        captured_token = _request_token.get()
        return MagicMock()

    request = _make_http_request({
        "authorization": "Bearer bearer-wins",
        "x-paperless-token": "x-header-loses",
        "x-paperless-url": "http://x",
    })
    transport_mock = _make_transport_mock("http")

    with patch("fastmcp.server.context._current_transport", transport_mock), \
         patch("fastmcp.server.dependencies.get_http_request", return_value=request), \
         patch("easypaperless_mcp.server.SERVER_URL", None):
        await middleware.on_call_tool(context, capture)

    assert captured_token == "bearer-wins"


@pytest.mark.asyncio
async def test_http_non_bearer_authorization_header_ignored(middleware, context):
    """Authorization header with non-Bearer scheme must be ignored; token falls back to None."""
    captured_token = "sentinel"

    async def capture(ctx):
        nonlocal captured_token
        captured_token = _request_token.get()
        return MagicMock()

    request = _make_http_request({"authorization": "Basic dXNlcjpwYXNz", "x-paperless-url": "http://x"})
    transport_mock = _make_transport_mock("http")

    with patch("fastmcp.server.context._current_transport", transport_mock), \
         patch("fastmcp.server.dependencies.get_http_request", return_value=request), \
         patch("easypaperless_mcp.server.SERVER_URL", None):
        await middleware.on_call_tool(context, capture)

    assert captured_token is None


@pytest.mark.asyncio
async def test_http_x_paperless_token_emits_deprecation_warning(middleware, context, caplog):
    """Using X-Paperless-Token must emit a deprecation warning in the server log."""
    import logging

    async def capture(ctx):
        return MagicMock()

    request = _make_http_request({"x-paperless-token": "old-token", "x-paperless-url": "http://x"})
    transport_mock = _make_transport_mock("http")

    with patch("fastmcp.server.context._current_transport", transport_mock), \
         patch("fastmcp.server.dependencies.get_http_request", return_value=request), \
         patch("easypaperless_mcp.server.SERVER_URL", None), \
         caplog.at_level(logging.WARNING, logger="easypaperless_mcp.server"):
        await middleware.on_call_tool(context, capture)

    assert any("deprecated" in record.message.lower() for record in caplog.records)
    assert any("Authorization" in record.message for record in caplog.records)


@pytest.mark.asyncio
async def test_http_bearer_no_deprecation_warning(middleware, context, caplog):
    """Using Authorization: Bearer must NOT emit a deprecation warning."""
    import logging

    async def capture(ctx):
        return MagicMock()

    request = _make_http_request({"authorization": "Bearer clean-token", "x-paperless-url": "http://x"})
    transport_mock = _make_transport_mock("http")

    with patch("fastmcp.server.context._current_transport", transport_mock), \
         patch("fastmcp.server.dependencies.get_http_request", return_value=request), \
         patch("easypaperless_mcp.server.SERVER_URL", None), \
         caplog.at_level(logging.WARNING, logger="easypaperless_mcp.server"):
        await middleware.on_call_tool(context, capture)

    assert not caplog.records


# ---------------------------------------------------------------------------
# ContextVar cleanup on exception
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_contextvars_reset_on_exception(middleware, context, monkeypatch):
    """ContextVars must be reset even when call_next raises."""
    monkeypatch.setenv("PAPERLESS_TOKEN", "env-token")
    monkeypatch.setenv("PAPERLESS_URL", "http://localhost:8000")

    async def raise_error(ctx):
        raise RuntimeError("tool failed")

    transport_mock = _make_transport_mock("stdio")
    with patch("fastmcp.server.context._current_transport", transport_mock):
        with pytest.raises(RuntimeError, match="tool failed"):
            await middleware.on_call_tool(context, raise_error)

    assert _request_token.get() is None
    assert _request_url.get() is None
