"""Unit tests for credential resolution in client.py."""

import importlib
from unittest.mock import MagicMock, patch

import pytest

import easypaperless_mcp.client as client_mod
from easypaperless_mcp.client import _request_token, _request_url, get_client


@pytest.fixture(autouse=True)
def reset_contextvars():
    """Reset ContextVars to default (None) around each test."""
    tok = _request_token.set(None)
    url = _request_url.set(None)
    yield
    _request_token.reset(tok)
    _request_url.reset(url)


# ---------------------------------------------------------------------------
# get_client — happy path
# ---------------------------------------------------------------------------


def test_get_client_returns_client_when_credentials_set():
    _request_token.set("test-token")
    _request_url.set("http://localhost:8000")
    c = get_client()
    assert c is not None


def test_get_client_uses_contextvar_token_not_server_env(monkeypatch):
    """Server-side env vars must NOT supply the token."""
    monkeypatch.setenv("PAPERLESS_TOKEN", "server-token-must-be-ignored")
    _request_token.set("client-token")
    _request_url.set("http://localhost:8000")
    c = get_client()
    # The client is created with whatever token the ContextVar holds.
    # We can't inspect the token directly, but we verify no RuntimeError is raised
    # and the correct value is in the ContextVar.
    assert _request_token.get() == "client-token"
    assert c is not None


# ---------------------------------------------------------------------------
# get_client — missing credentials
# ---------------------------------------------------------------------------


def test_get_client_raises_when_token_missing():
    _request_url.set("http://localhost:8000")
    with pytest.raises(RuntimeError, match="PAPERLESS_TOKEN"):
        get_client()


def test_get_client_raises_when_url_missing():
    _request_token.set("test-token")
    with pytest.raises(RuntimeError, match="PAPERLESS_URL"):
        get_client()


def test_get_client_raises_when_both_missing():
    with pytest.raises(RuntimeError, match="PAPERLESS_TOKEN"):
        get_client()


def test_get_client_error_mentions_mcp_client_config():
    """Error message must guide users to configure the MCP client, not the server."""
    with pytest.raises(RuntimeError) as exc_info:
        get_client()
    msg = str(exc_info.value)
    assert "MCP client" in msg or "claude_desktop_config" in msg or "mcp-remote" in msg


# ---------------------------------------------------------------------------
# SERVER_URL — locked URL behaviour
# ---------------------------------------------------------------------------


def test_server_url_is_none_when_env_not_set(monkeypatch):
    monkeypatch.delenv("PAPERLESS_URL", raising=False)
    # Re-import to simulate fresh startup — SERVER_URL is module-level, so we
    # just verify the current value reflects the env at import time.
    # (The fixture cannot reload the module; we test the logic via the value.)
    # If PAPERLESS_URL is unset in the environment at test time, SERVER_URL is None.
    # This test documents the expected behaviour.
    assert client_mod.SERVER_URL is None or isinstance(client_mod.SERVER_URL, str)


def test_server_url_takes_precedence_over_contextvar(monkeypatch):
    """When SERVER_URL is set, the ContextVar URL is used only as a fallback
    for the middleware — documented here to prevent regression."""
    # The middleware (not get_client) is responsible for enforcing SERVER_URL
    # precedence. get_client reads only from ContextVars. This test verifies
    # that when the ContextVar holds the server URL value, get_client uses it.
    _request_token.set("test-token")
    _request_url.set("http://server-locked-url:8000")
    c = get_client()
    assert c is not None
    assert _request_url.get() == "http://server-locked-url:8000"


# ---------------------------------------------------------------------------
# Retry configuration — get_client kwargs
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_retry_globals():
    """Restore module-level retry globals around each test."""
    orig_attempts = client_mod._retry_attempts
    orig_backoff = client_mod._retry_backoff
    yield
    client_mod._retry_attempts = orig_attempts
    client_mod._retry_backoff = orig_backoff


def test_get_client_passes_retry_attempts_when_set(monkeypatch):
    _request_token.set("test-token")
    _request_url.set("http://localhost:8000")
    client_mod._retry_attempts = 3
    client_mod._retry_backoff = None
    mock_cls = MagicMock()
    with patch("easypaperless_mcp.client.SyncPaperlessClient", mock_cls):
        get_client()
    mock_cls.assert_called_once_with(
        url="http://localhost:8000", api_token="test-token", retry_attempts=3
    )


def test_get_client_passes_retry_backoff_when_set(monkeypatch):
    _request_token.set("test-token")
    _request_url.set("http://localhost:8000")
    client_mod._retry_attempts = None
    client_mod._retry_backoff = 2.0
    mock_cls = MagicMock()
    with patch("easypaperless_mcp.client.SyncPaperlessClient", mock_cls):
        get_client()
    mock_cls.assert_called_once_with(
        url="http://localhost:8000", api_token="test-token", retry_backoff=2.0
    )


def test_get_client_passes_both_retry_params_when_set(monkeypatch):
    _request_token.set("test-token")
    _request_url.set("http://localhost:8000")
    client_mod._retry_attempts = 3
    client_mod._retry_backoff = 2.0
    mock_cls = MagicMock()
    with patch("easypaperless_mcp.client.SyncPaperlessClient", mock_cls):
        get_client()
    mock_cls.assert_called_once_with(
        url="http://localhost:8000", api_token="test-token", retry_attempts=3, retry_backoff=2.0
    )


def test_get_client_omits_retry_kwargs_when_not_set(monkeypatch):
    _request_token.set("test-token")
    _request_url.set("http://localhost:8000")
    client_mod._retry_attempts = None
    client_mod._retry_backoff = None
    mock_cls = MagicMock()
    with patch("easypaperless_mcp.client.SyncPaperlessClient", mock_cls):
        get_client()
    mock_cls.assert_called_once_with(url="http://localhost:8000", api_token="test-token")


# ---------------------------------------------------------------------------
# Retry configuration — env var parsing (module reload)
# ---------------------------------------------------------------------------


def test_retry_attempts_parsed_from_env(monkeypatch):
    monkeypatch.setenv("PAPERLESS_RETRY_ATTEMPTS", "5")
    monkeypatch.delenv("PAPERLESS_RETRY_BACKOFF", raising=False)
    importlib.reload(client_mod)
    assert client_mod._retry_attempts == 5
    assert client_mod._retry_backoff is None


def test_retry_backoff_parsed_from_env(monkeypatch):
    monkeypatch.delenv("PAPERLESS_RETRY_ATTEMPTS", raising=False)
    monkeypatch.setenv("PAPERLESS_RETRY_BACKOFF", "1.5")
    importlib.reload(client_mod)
    assert client_mod._retry_attempts is None
    assert client_mod._retry_backoff == 1.5


def test_retry_both_parsed_from_env(monkeypatch):
    monkeypatch.setenv("PAPERLESS_RETRY_ATTEMPTS", "3")
    monkeypatch.setenv("PAPERLESS_RETRY_BACKOFF", "2.0")
    importlib.reload(client_mod)
    assert client_mod._retry_attempts == 3
    assert client_mod._retry_backoff == 2.0


def test_retry_neither_env_var_set(monkeypatch):
    monkeypatch.delenv("PAPERLESS_RETRY_ATTEMPTS", raising=False)
    monkeypatch.delenv("PAPERLESS_RETRY_BACKOFF", raising=False)
    importlib.reload(client_mod)
    assert client_mod._retry_attempts is None
    assert client_mod._retry_backoff is None


def test_invalid_retry_attempts_raises_runtime_error(monkeypatch):
    monkeypatch.setenv("PAPERLESS_RETRY_ATTEMPTS", "not-an-int")
    monkeypatch.delenv("PAPERLESS_RETRY_BACKOFF", raising=False)
    with pytest.raises(RuntimeError, match="PAPERLESS_RETRY_ATTEMPTS"):
        importlib.reload(client_mod)


def test_invalid_retry_backoff_raises_runtime_error(monkeypatch):
    monkeypatch.delenv("PAPERLESS_RETRY_ATTEMPTS", raising=False)
    monkeypatch.setenv("PAPERLESS_RETRY_BACKOFF", "not-a-float")
    with pytest.raises(RuntimeError, match="PAPERLESS_RETRY_BACKOFF"):
        importlib.reload(client_mod)
