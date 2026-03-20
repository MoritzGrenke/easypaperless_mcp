"""Integration tests for users tools against a live paperless-ngx instance."""

import pytest
from easypaperless import SyncPaperlessClient, User

from easypaperless_mcp.tools.models import ListResult
from easypaperless_mcp.tools.users import get_user, list_users


pytestmark = pytest.mark.integration


def test_list_users_returns_list_result(paperless_client: SyncPaperlessClient) -> None:
    result = list_users()
    assert isinstance(result, ListResult)
    assert isinstance(result.count, int)
    assert isinstance(result.items, list)


def test_list_users_returns_user_objects(paperless_client: SyncPaperlessClient) -> None:
    result = list_users()
    for user in result.items:
        assert isinstance(user, User)


def test_get_user_round_trip(paperless_client: SyncPaperlessClient) -> None:
    result = list_users()
    if not result.items:
        pytest.skip("No users in test instance")
    user_id = result.items[0].id
    assert user_id is not None
    fetched = get_user(user_id)
    assert fetched.id == user_id
