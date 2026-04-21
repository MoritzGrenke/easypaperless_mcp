"""Unit tests for document history sub-server tools."""

from datetime import datetime, timezone
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from easypaperless import AuditLogEntry

from easypaperless_mcp.tools.document_history import get_document_history
from easypaperless_mcp.tools.models import ListResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def patch_document_history_get_client(patch_get_client: MagicMock):
    """Patch get_client inside the document_history module."""
    with patch("easypaperless_mcp.tools.document_history.get_client", return_value=patch_get_client):
        yield patch_get_client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_audit_log_entry(**kwargs: Any) -> AuditLogEntry:
    """Build a minimal AuditLogEntry with sensible defaults."""
    defaults: dict[str, Any] = {
        "id": 1,
        "timestamp": datetime(2024, 1, 1, tzinfo=timezone.utc),
        "action": "create",
        "changes": {},
        "actor": None,
    }
    defaults.update(kwargs)
    return AuditLogEntry.model_validate(defaults)


def make_paged_result(entries: list[AuditLogEntry]) -> MagicMock:
    """Build a minimal PagedResult mock."""
    paged: MagicMock = MagicMock()
    paged.results = entries
    paged.count = len(entries)
    return paged


# ---------------------------------------------------------------------------
# get_document_history
# ---------------------------------------------------------------------------


def test_get_document_history_calls_client(patch_get_client: MagicMock) -> None:
    entries = [make_audit_log_entry(id=1), make_audit_log_entry(id=2)]
    patch_get_client.documents.history.return_value = make_paged_result(entries)
    result = get_document_history(id=42)
    patch_get_client.documents.history.assert_called_once_with(42, page=None, page_size=None)
    assert result.count == 2
    assert len(result.items) == 2


def test_get_document_history_returns_list_result(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.history.return_value = make_paged_result([])
    result = get_document_history(id=1)
    assert isinstance(result, ListResult)
    assert result.count == 0
    assert result.items == []


def test_get_document_history_returns_audit_log_entry_objects(patch_get_client: MagicMock) -> None:
    entry = make_audit_log_entry(id=7, action="update", changes={"title": ["old", "new"]})
    patch_get_client.documents.history.return_value = make_paged_result([entry])
    result = get_document_history(id=42)
    assert isinstance(result.items[0], AuditLogEntry)
    assert result.items[0].id == 7
    assert result.items[0].action == "update"


def test_get_document_history_passes_pagination_params(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.history.return_value = make_paged_result([])
    get_document_history(id=5, page=2, page_size=10)
    patch_get_client.documents.history.assert_called_once_with(5, page=2, page_size=10)


def test_get_document_history_passes_correct_document_id(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.history.return_value = make_paged_result([])
    get_document_history(id=99)
    call_args = patch_get_client.documents.history.call_args
    assert call_args.args[0] == 99


def test_get_document_history_empty_history(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.history.return_value = make_paged_result([])
    result = get_document_history(id=42)
    assert result.count == 0
    assert result.items == []


def test_get_document_history_count_matches_total_not_page(patch_get_client: MagicMock) -> None:
    """count reflects the total from PagedResult, not just items on this page."""
    paged = MagicMock()
    paged.results = [make_audit_log_entry(id=1)]
    paged.count = 50
    patch_get_client.documents.history.return_value = paged
    result = get_document_history(id=1)
    assert result.count == 50
    assert len(result.items) == 1
