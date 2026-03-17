"""Integration tests for custom fields tools against a live paperless-ngx instance."""

import pytest
from easypaperless import CustomField, SyncPaperlessClient

from easypaperless_mcp.tools.custom_fields import get_custom_field, list_custom_fields
from easypaperless_mcp.tools.models import ListResult


pytestmark = pytest.mark.integration


def test_list_custom_fields_returns_list_result(paperless_client: SyncPaperlessClient) -> None:
    result = list_custom_fields()
    assert isinstance(result, ListResult)
    assert isinstance(result.count, int)
    assert isinstance(result.items, list)


def test_list_custom_fields_returns_custom_field_objects(paperless_client: SyncPaperlessClient) -> None:
    result = list_custom_fields()
    for field in result.items:
        assert isinstance(field, CustomField)


def test_get_custom_field_round_trip(paperless_client: SyncPaperlessClient) -> None:
    result = list_custom_fields()
    if not result.items:
        pytest.skip("No custom fields in test instance")
    field_id = result.items[0].id
    assert field_id is not None
    fetched = get_custom_field(field_id)
    assert fetched.id == field_id
