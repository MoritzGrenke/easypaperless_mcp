"""Integration test fixtures — require a live paperless-ngx instance."""

import os
from collections.abc import Generator

import pytest
from easypaperless import SyncPaperlessClient

from easypaperless_mcp.client import _request_token, _request_url


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "integration: mark test as requiring a live paperless-ngx instance")


@pytest.fixture(scope="session", autouse=True)
def require_env() -> None:
    """Skip all integration tests when env vars are absent."""
    if not os.environ.get("PAPERLESS_URL") or not os.environ.get("PAPERLESS_TOKEN"):
        pytest.skip(
            "Integration tests require PAPERLESS_URL and PAPERLESS_TOKEN env vars",
            allow_module_level=True,
        )


@pytest.fixture(scope="session", autouse=True)
def set_contextvars(require_env: None) -> Generator[None, None, None]:
    """Populate ContextVars from env vars so tool functions can call get_client().

    Tool functions call get_client() which reads from _request_token/_request_url
    ContextVars (set by CredentialMiddleware in production). Integration tests call
    tools directly, bypassing the middleware, so we seed the ContextVars here.
    """
    tok = _request_token.set(os.environ["PAPERLESS_TOKEN"])
    url_tok = _request_url.set(os.environ["PAPERLESS_URL"])
    yield
    _request_token.reset(tok)
    _request_url.reset(url_tok)


@pytest.fixture(scope="session")
def paperless_client() -> SyncPaperlessClient:
    """Return a real SyncPaperlessClient for the test instance."""
    return SyncPaperlessClient(
        url=os.environ["PAPERLESS_URL"],
        api_token=os.environ["PAPERLESS_TOKEN"],
    )
