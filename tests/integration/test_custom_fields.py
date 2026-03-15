"""Integration tests for custom fields tools against a live paperless-ngx instance."""

import pytest
from easypaperless import CustomField, SyncPaperlessClient

from easypaperless_mcp.tools.custom_fields import get_custom_field, list_custom_fields


pytestmark = pytest.mark.integration


def test_list_custom_fields_returns_list(paperless_client: SyncPaperlessClient) -> None:
    result = list_custom_fields()
    assert isinstance(result, list)


def test_list_custom_fields_returns_custom_field_objects(paperless_client: SyncPaperlessClient) -> None:
    result = list_custom_fields()
    for field in result:
        assert isinstance(field, CustomField)


def test_get_custom_field_round_trip(paperless_client: SyncPaperlessClient) -> None:
    fields = list_custom_fields()
    if not fields:
        pytest.skip("No custom fields in test instance")
    field_id = fields[0].id
    assert field_id is not None
    fetched = get_custom_field(field_id)
    assert fetched.id == field_id
