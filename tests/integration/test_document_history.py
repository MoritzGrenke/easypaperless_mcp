"""Integration tests for document history tools against a live paperless-ngx instance."""

import pytest
from easypaperless import AuditLogEntry, SyncPaperlessClient

from easypaperless_mcp.tools.document_history import get_document_history
from easypaperless_mcp.tools.documents import list_documents
from easypaperless_mcp.tools.models import ListResult


pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def document_id(paperless_client: SyncPaperlessClient) -> int:
    """Return the ID of the first available document, skipping if none exist."""
    result = list_documents()
    if not result.items:
        pytest.skip("No documents in test instance")
    assert result.items[0].id is not None
    return result.items[0].id


def test_get_document_history_returns_list_result(
    paperless_client: SyncPaperlessClient, document_id: int
) -> None:
    result = get_document_history(id=document_id)
    assert isinstance(result, ListResult)


def test_get_document_history_returns_count(
    paperless_client: SyncPaperlessClient, document_id: int
) -> None:
    result = get_document_history(id=document_id)
    assert isinstance(result.count, int)
    assert result.count >= 0


def test_get_document_history_returns_audit_log_entry_objects(
    paperless_client: SyncPaperlessClient, document_id: int
) -> None:
    result = get_document_history(id=document_id)
    for entry in result.items:
        assert isinstance(entry, AuditLogEntry)


def test_get_document_history_pagination_params_accepted(
    paperless_client: SyncPaperlessClient, document_id: int
) -> None:
    """page and page_size parameters should be accepted without error."""
    result = get_document_history(id=document_id, page=1, page_size=10)
    assert isinstance(result, ListResult)
