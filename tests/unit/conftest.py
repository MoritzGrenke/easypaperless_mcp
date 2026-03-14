"""Unit test fixtures — all external calls are mocked."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from easypaperless import Document


@pytest.fixture
def mock_client() -> MagicMock:
    """Return a MagicMock that replaces SyncPaperlessClient."""
    return MagicMock()


@pytest.fixture(autouse=True)
def patch_get_client(mock_client: MagicMock):
    """Patch get_client() globally for every unit test."""
    with patch("easypaperless_mcp.client.get_client", return_value=mock_client):
        with patch("easypaperless_mcp.tools.documents.get_client", return_value=mock_client):
            yield mock_client


def make_document(**kwargs: Any) -> Document:
    """Build a minimal Document with sensible defaults."""
    defaults: dict[str, Any] = {
        "id": 1,
        "title": "Test Document",
        "created": "2024-01-01",
        "correspondent": None,
        "document_type": None,
        "storage_path": None,
        "tags": [],
        "custom_fields": [],
        "notes": [],
        "archive_serial_number": None,
        "original_file_name": "test.pdf",
        "content": "some content",
        "added": "2024-01-01",
        "modified": "2024-01-01",
    }
    defaults.update(kwargs)
    return Document.model_validate(defaults)
