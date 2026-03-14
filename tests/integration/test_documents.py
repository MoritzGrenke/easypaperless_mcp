"""Integration tests for documents tools against a live paperless-ngx instance."""

import pytest
from easypaperless import SyncPaperlessClient

from easypaperless_mcp.tools.documents import get_document, list_documents


pytestmark = pytest.mark.integration


def test_list_documents_returns_list(paperless_client: SyncPaperlessClient) -> None:
    result = list_documents(max_results=5)
    assert isinstance(result, list)


def test_list_documents_search(paperless_client: SyncPaperlessClient) -> None:
    result = list_documents(search="a", max_results=5)
    assert isinstance(result, list)


def test_get_document_round_trip(paperless_client: SyncPaperlessClient) -> None:
    docs = list_documents(max_results=1)
    if not docs:
        pytest.skip("No documents in test instance")
    doc_id = docs[0].id
    assert doc_id is not None
    fetched = get_document(doc_id)
    assert fetched.id == doc_id
