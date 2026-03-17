"""Integration tests for tags tools against a live paperless-ngx instance."""

import pytest
from easypaperless import SyncPaperlessClient, Tag

from easypaperless_mcp.tools.models import ListResult
from easypaperless_mcp.tools.tags import get_tag, list_tags


pytestmark = pytest.mark.integration


def test_list_tags_returns_list_result(paperless_client: SyncPaperlessClient) -> None:
    result = list_tags()
    assert isinstance(result, ListResult)
    assert isinstance(result.count, int)
    assert isinstance(result.items, list)


def test_list_tags_returns_tag_objects(paperless_client: SyncPaperlessClient) -> None:
    result = list_tags()
    for tag in result.items:
        assert isinstance(tag, Tag)


def test_get_tag_round_trip(paperless_client: SyncPaperlessClient) -> None:
    result = list_tags()
    if not result.items:
        pytest.skip("No tags in test instance")
    tag_id = result.items[0].id
    assert tag_id is not None
    fetched = get_tag(tag_id)
    assert fetched.id == tag_id
