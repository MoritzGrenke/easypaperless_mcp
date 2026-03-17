"""Integration tests for documents tools against a live paperless-ngx instance."""

import pytest
from easypaperless import SyncPaperlessClient

from easypaperless_mcp.tools.documents import get_document, list_documents
from easypaperless_mcp.tools.models import ListResult


pytestmark = pytest.mark.integration


def test_list_documents_returns_list_result(paperless_client: SyncPaperlessClient) -> None:
    result = list_documents(max_results=5)
    assert isinstance(result, ListResult)
    assert isinstance(result.count, int)
    assert isinstance(result.items, list)


def test_list_documents_search(paperless_client: SyncPaperlessClient) -> None:
    result = list_documents(search="a", max_results=5)
    assert isinstance(result, ListResult)


def test_get_document_round_trip(paperless_client: SyncPaperlessClient) -> None:
    result = list_documents(max_results=1)
    if not result.items:
        pytest.skip("No documents in test instance")
    doc_id = result.items[0].id
    assert doc_id is not None
    fetched = get_document(doc_id)
    assert fetched.id == doc_id
