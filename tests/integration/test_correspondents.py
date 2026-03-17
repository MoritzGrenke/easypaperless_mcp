"""Integration tests for correspondents tools against a live paperless-ngx instance."""

import pytest
from easypaperless import Correspondent, SyncPaperlessClient

from easypaperless_mcp.tools.correspondents import get_correspondent, list_correspondents
from easypaperless_mcp.tools.models import ListResult


pytestmark = pytest.mark.integration


def test_list_correspondents_returns_list_result(paperless_client: SyncPaperlessClient) -> None:
    result = list_correspondents()
    assert isinstance(result, ListResult)
    assert isinstance(result.count, int)
    assert isinstance(result.items, list)


def test_list_correspondents_returns_correspondent_objects(paperless_client: SyncPaperlessClient) -> None:
    result = list_correspondents()
    for correspondent in result.items:
        assert isinstance(correspondent, Correspondent)


def test_get_correspondent_round_trip(paperless_client: SyncPaperlessClient) -> None:
    result = list_correspondents()
    if not result.items:
        pytest.skip("No correspondents in test instance")
    correspondent_id = result.items[0].id
    assert correspondent_id is not None
    fetched = get_correspondent(correspondent_id)
    assert fetched.id == correspondent_id
