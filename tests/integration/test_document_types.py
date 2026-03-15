"""Integration tests for document types tools against a live paperless-ngx instance."""

import pytest
from easypaperless import DocumentType, SyncPaperlessClient

from easypaperless_mcp.tools.document_types import get_document_type, list_document_types


pytestmark = pytest.mark.integration


def test_list_document_types_returns_list(paperless_client: SyncPaperlessClient) -> None:
    result = list_document_types()
    assert isinstance(result, list)


def test_list_document_types_returns_document_type_objects(paperless_client: SyncPaperlessClient) -> None:
    result = list_document_types()
    for document_type in result:
        assert isinstance(document_type, DocumentType)


def test_get_document_type_round_trip(paperless_client: SyncPaperlessClient) -> None:
    document_types = list_document_types()
    if not document_types:
        pytest.skip("No document types in test instance")
    document_type_id = document_types[0].id
    assert document_type_id is not None
    fetched = get_document_type(document_type_id)
    assert fetched.id == document_type_id
