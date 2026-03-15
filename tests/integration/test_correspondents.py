"""Integration tests for correspondents tools against a live paperless-ngx instance."""

import pytest
from easypaperless import Correspondent, SyncPaperlessClient

from easypaperless_mcp.tools.correspondents import get_correspondent, list_correspondents


pytestmark = pytest.mark.integration


def test_list_correspondents_returns_list(paperless_client: SyncPaperlessClient) -> None:
    result = list_correspondents()
    assert isinstance(result, list)


def test_list_correspondents_returns_correspondent_objects(paperless_client: SyncPaperlessClient) -> None:
    result = list_correspondents()
    for correspondent in result:
        assert isinstance(correspondent, Correspondent)


def test_get_correspondent_round_trip(paperless_client: SyncPaperlessClient) -> None:
    correspondents = list_correspondents()
    if not correspondents:
        pytest.skip("No correspondents in test instance")
    correspondent_id = correspondents[0].id
    assert correspondent_id is not None
    fetched = get_correspondent(correspondent_id)
    assert fetched.id == correspondent_id
