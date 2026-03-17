"""Integration tests for document types tools against a live paperless-ngx instance."""

import pytest
from easypaperless import DocumentType, SyncPaperlessClient

from easypaperless_mcp.tools.document_types import get_document_type, list_document_types
from easypaperless_mcp.tools.models import ListResult


pytestmark = pytest.mark.integration


def test_list_document_types_returns_list_result(paperless_client: SyncPaperlessClient) -> None:
    result = list_document_types()
    assert isinstance(result, ListResult)
    assert isinstance(result.count, int)
    assert isinstance(result.items, list)


def test_list_document_types_returns_document_type_objects(paperless_client: SyncPaperlessClient) -> None:
    result = list_document_types()
    for document_type in result.items:
        assert isinstance(document_type, DocumentType)


def test_get_document_type_round_trip(paperless_client: SyncPaperlessClient) -> None:
    result = list_document_types()
    if not result.items:
        pytest.skip("No document types in test instance")
    document_type_id = result.items[0].id
    assert document_type_id is not None
    fetched = get_document_type(document_type_id)
    assert fetched.id == document_type_id
