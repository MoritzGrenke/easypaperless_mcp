"""Integration tests for tags tools against a live paperless-ngx instance."""

import pytest
from easypaperless import SyncPaperlessClient, Tag

from easypaperless_mcp.tools.tags import get_tag, list_tags


pytestmark = pytest.mark.integration


def test_list_tags_returns_list(paperless_client: SyncPaperlessClient) -> None:
    result = list_tags()
    assert isinstance(result, list)


def test_list_tags_returns_tag_objects(paperless_client: SyncPaperlessClient) -> None:
    result = list_tags()
    for tag in result:
        assert isinstance(tag, Tag)


def test_get_tag_round_trip(paperless_client: SyncPaperlessClient) -> None:
    tags = list_tags()
    if not tags:
        pytest.skip("No tags in test instance")
    tag_id = tags[0].id
    assert tag_id is not None
    fetched = get_tag(tag_id)
    assert fetched.id == tag_id
