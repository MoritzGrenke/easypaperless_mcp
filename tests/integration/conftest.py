"""Integration test fixtures — require a live paperless-ngx instance."""

import os

import pytest
from easypaperless import SyncPaperlessClient

import easypaperless_mcp.client as _client_module


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


@pytest.fixture(scope="session")
def paperless_client() -> SyncPaperlessClient:
    """Return a real SyncPaperlessClient for the test instance."""
    _client_module._client = None  # reset singleton so env vars are picked up
    return _client_module.get_client()
