"""Integration tests for trash tools against a live paperless-ngx instance."""

import pytest
from easypaperless import Document, SyncPaperlessClient

from easypaperless_mcp.tools.models import ListResult
from easypaperless_mcp.tools.trash import list_trash


pytestmark = pytest.mark.integration


def test_list_trash_returns_list_result(paperless_client: SyncPaperlessClient) -> None:
    result = list_trash()
    assert isinstance(result, ListResult)
    assert isinstance(result.count, int)
    assert isinstance(result.items, list)


def test_list_trash_returns_document_objects(paperless_client: SyncPaperlessClient) -> None:
    result = list_trash()
    for doc in result.items:
        assert isinstance(doc, Document)


def test_list_trash_with_pagination(paperless_client: SyncPaperlessClient) -> None:
    result = list_trash(page=1, page_size=5)
    assert isinstance(result, ListResult)
    assert isinstance(result.count, int)
    assert len(result.items) <= 5
