"""Unit tests for custom fields sub-server tools."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from easypaperless import CustomField, SetPermissions

from easypaperless_mcp.tools.custom_fields import (
    create_custom_field,
    delete_custom_field,
    get_custom_field,
    list_custom_fields,
    update_custom_field,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def patch_custom_fields_get_client(patch_get_client: MagicMock):
    """Also patch get_client inside the custom_fields module."""
    with patch("easypaperless_mcp.tools.custom_fields.get_client", return_value=patch_get_client):
        yield patch_get_client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_custom_field(**kwargs: Any) -> CustomField:
    """Build a minimal CustomField with sensible defaults."""
    defaults: dict[str, Any] = {
        "id": 1,
        "name": "Test Field",
        "data_type": "string",
    }
    defaults.update(kwargs)
    return CustomField.model_validate(defaults)


# ---------------------------------------------------------------------------
# list_custom_fields
# ---------------------------------------------------------------------------


def test_list_custom_fields_calls_client(patch_get_client: MagicMock) -> None:
    patch_get_client.custom_fields.list.return_value = [make_custom_field(id=1), make_custom_field(id=2)]
    result = list_custom_fields()
    patch_get_client.custom_fields.list.assert_called_once()
    assert len(result) == 2


def test_list_custom_fields_returns_empty_list(patch_get_client: MagicMock) -> None:
    patch_get_client.custom_fields.list.return_value = []
    assert list_custom_fields() == []


def test_list_custom_fields_passes_name_contains(patch_get_client: MagicMock) -> None:
    patch_get_client.custom_fields.list.return_value = []
    list_custom_fields(name_contains="invoice")
    assert patch_get_client.custom_fields.list.call_args.kwargs["name_contains"] == "invoice"


def test_list_custom_fields_passes_name_exact(patch_get_client: MagicMock) -> None:
    patch_get_client.custom_fields.list.return_value = []
    list_custom_fields(name_exact="Invoice Amount")
    assert patch_get_client.custom_fields.list.call_args.kwargs["name_exact"] == "Invoice Amount"


def test_list_custom_fields_passes_pagination_params(patch_get_client: MagicMock) -> None:
    patch_get_client.custom_fields.list.return_value = []
    list_custom_fields(page=2, page_size=50, ordering="name", descending=True)
    call_kwargs = patch_get_client.custom_fields.list.call_args.kwargs
    assert call_kwargs["page"] == 2
    assert call_kwargs["page_size"] == 50
    assert call_kwargs["ordering"] == "name"
    assert call_kwargs["descending"] is True


def test_list_custom_fields_omits_none_optional_params(patch_get_client: MagicMock) -> None:
    patch_get_client.custom_fields.list.return_value = []
    list_custom_fields()
    call_kwargs = patch_get_client.custom_fields.list.call_args.kwargs
    assert "name_contains" not in call_kwargs
    assert "name_exact" not in call_kwargs
    assert "page" not in call_kwargs
    assert "page_size" not in call_kwargs
    assert "ordering" not in call_kwargs


def test_list_custom_fields_has_no_ids_param(patch_get_client: MagicMock) -> None:
    """list_custom_fields has no ids filter — unlike correspondents/tags."""
    import inspect
    sig = inspect.signature(list_custom_fields)
    assert "ids" not in sig.parameters


def test_list_custom_fields_returns_custom_field_objects(patch_get_client: MagicMock) -> None:
    patch_get_client.custom_fields.list.return_value = [make_custom_field(id=5, name="Amount")]
    result = list_custom_fields()
    assert isinstance(result[0], CustomField)
    assert result[0].id == 5
    assert result[0].name == "Amount"


# ---------------------------------------------------------------------------
# get_custom_field
# ---------------------------------------------------------------------------


def test_get_custom_field_calls_client(patch_get_client: MagicMock) -> None:
    patch_get_client.custom_fields.get.return_value = make_custom_field(id=7)
    result = get_custom_field(7)
    patch_get_client.custom_fields.get.assert_called_once_with(id=7)
    assert result.id == 7


def test_get_custom_field_returns_custom_field(patch_get_client: MagicMock) -> None:
    patch_get_client.custom_fields.get.return_value = make_custom_field(id=3, name="Due Date")
    result = get_custom_field(3)
    assert isinstance(result, CustomField)
    assert result.name == "Due Date"


# ---------------------------------------------------------------------------
# create_custom_field
# ---------------------------------------------------------------------------


def test_create_custom_field_minimal(patch_get_client: MagicMock) -> None:
    patch_get_client.custom_fields.create.return_value = make_custom_field(id=10, name="Amount", data_type="monetary")
    result = create_custom_field(name="Amount", data_type="monetary")
    patch_get_client.custom_fields.create.assert_called_once()
    call_kwargs = patch_get_client.custom_fields.create.call_args.kwargs
    assert call_kwargs["name"] == "Amount"
    assert call_kwargs["data_type"] == "monetary"
    assert result.id == 10


def test_create_custom_field_passes_all_params(patch_get_client: MagicMock) -> None:
    patch_get_client.custom_fields.create.return_value = make_custom_field(id=11)
    perms = MagicMock(spec=SetPermissions)
    create_custom_field(
        name="Category",
        data_type="select",
        extra_data={"options": ["A", "B"]},
        owner=5,
        set_permissions=perms,
    )
    call_kwargs = patch_get_client.custom_fields.create.call_args.kwargs
    assert call_kwargs["name"] == "Category"
    assert call_kwargs["data_type"] == "select"
    assert call_kwargs["extra_data"] == {"options": ["A", "B"]}
    assert call_kwargs["owner"] == 5
    assert call_kwargs["set_permissions"] is perms


def test_create_custom_field_omits_none_optional_params(patch_get_client: MagicMock) -> None:
    patch_get_client.custom_fields.create.return_value = make_custom_field(id=1)
    create_custom_field(name="Minimal", data_type="string")
    call_kwargs = patch_get_client.custom_fields.create.call_args.kwargs
    assert "extra_data" not in call_kwargs
    assert "owner" not in call_kwargs
    assert "set_permissions" not in call_kwargs


def test_create_custom_field_returns_custom_field(patch_get_client: MagicMock) -> None:
    patch_get_client.custom_fields.create.return_value = make_custom_field(id=20, name="Created")
    result = create_custom_field(name="Created", data_type="boolean")
    assert isinstance(result, CustomField)
    assert result.name == "Created"


# ---------------------------------------------------------------------------
# update_custom_field
# ---------------------------------------------------------------------------


def test_update_custom_field_passes_provided_fields(patch_get_client: MagicMock) -> None:
    patch_get_client.custom_fields.update.return_value = make_custom_field(id=1, name="Renamed")
    update_custom_field(1, name="Renamed")
    call_args = patch_get_client.custom_fields.update.call_args
    assert call_args.args[0] == 1
    assert call_args.kwargs.get("name") == "Renamed"


def test_update_custom_field_omits_unset_fields(patch_get_client: MagicMock) -> None:
    """Fields not passed must not be forwarded to the client (UNSET sentinel)."""
    patch_get_client.custom_fields.update.return_value = make_custom_field(id=1)
    update_custom_field(1, name="X")
    call_kwargs = patch_get_client.custom_fields.update.call_args.kwargs
    assert "data_type" not in call_kwargs
    assert "extra_data" not in call_kwargs


def test_update_custom_field_no_extra_kwargs_when_only_id(patch_get_client: MagicMock) -> None:
    patch_get_client.custom_fields.update.return_value = make_custom_field(id=1)
    update_custom_field(1)
    assert patch_get_client.custom_fields.update.call_args.kwargs == {}


def test_update_custom_field_passes_all_params(patch_get_client: MagicMock) -> None:
    patch_get_client.custom_fields.update.return_value = make_custom_field(id=5)
    update_custom_field(
        5,
        name="Updated",
        data_type="integer",
        extra_data={"min": 0},
    )
    call_kwargs = patch_get_client.custom_fields.update.call_args.kwargs
    assert call_kwargs["name"] == "Updated"
    assert call_kwargs["data_type"] == "integer"
    assert call_kwargs["extra_data"] == {"min": 0}


def test_update_custom_field_clears_nullable_fields_when_none_passed(patch_get_client: MagicMock) -> None:
    """Explicitly passing None must forward None to the client (clear the field)."""
    patch_get_client.custom_fields.update.return_value = make_custom_field(id=1)
    update_custom_field(1, extra_data=None)
    call_kwargs = patch_get_client.custom_fields.update.call_args.kwargs
    assert "extra_data" in call_kwargs
    assert call_kwargs["extra_data"] is None


def test_update_custom_field_returns_custom_field(patch_get_client: MagicMock) -> None:
    patch_get_client.custom_fields.update.return_value = make_custom_field(id=1, name="Updated")
    result = update_custom_field(1, name="Updated")
    assert isinstance(result, CustomField)


def test_update_custom_field_has_no_owner_or_set_permissions_params(patch_get_client: MagicMock) -> None:
    """update_custom_field does not support owner/set_permissions — unlike correspondents."""
    import inspect
    sig = inspect.signature(update_custom_field)
    assert "owner" not in sig.parameters
    assert "set_permissions" not in sig.parameters


# ---------------------------------------------------------------------------
# delete_custom_field
# ---------------------------------------------------------------------------


def test_delete_custom_field_calls_client(patch_get_client: MagicMock) -> None:
    delete_custom_field(99)
    patch_get_client.custom_fields.delete.assert_called_once_with(id=99)


def test_delete_custom_field_returns_none(patch_get_client: MagicMock) -> None:
    patch_get_client.custom_fields.delete.return_value = None
    result = delete_custom_field(1)
    assert result is None
