"""Unit tests for document types sub-server tools."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from easypaperless import DocumentType, MatchingAlgorithm, SetPermissions

from easypaperless_mcp.tools.document_types import (
    bulk_delete_document_types,
    bulk_set_document_type_permissions,
    create_document_type,
    delete_document_type,
    get_document_type,
    list_document_types,
    update_document_type,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def patch_document_types_get_client(patch_get_client: MagicMock):
    """Also patch get_client inside the document_types module."""
    with patch("easypaperless_mcp.tools.document_types.get_client", return_value=patch_get_client):
        yield patch_get_client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_document_type(**kwargs: Any) -> DocumentType:
    """Build a minimal DocumentType with sensible defaults."""
    defaults: dict[str, Any] = {
        "id": 1,
        "name": "Test Document Type",
    }
    defaults.update(kwargs)
    return DocumentType.model_validate(defaults)


# ---------------------------------------------------------------------------
# list_document_types
# ---------------------------------------------------------------------------


def test_list_document_types_calls_client(patch_get_client: MagicMock) -> None:
    patch_get_client.document_types.list.return_value = MagicMock(count=2, results=[make_document_type(id=1), make_document_type(id=2)])
    result = list_document_types()
    patch_get_client.document_types.list.assert_called_once()
    assert result.count == 2
    assert len(result.items) == 2


def test_list_document_types_returns_empty_list(patch_get_client: MagicMock) -> None:
    patch_get_client.document_types.list.return_value = MagicMock(count=0, results=[])
    result = list_document_types()
    assert result.count == 0
    assert result.items == []


def test_list_document_types_passes_ids(patch_get_client: MagicMock) -> None:
    patch_get_client.document_types.list.return_value = MagicMock(count=0, results=[])
    list_document_types(ids=[1, 2, 3])
    assert patch_get_client.document_types.list.call_args.kwargs["ids"] == [1, 2, 3]


def test_list_document_types_passes_name_contains(patch_get_client: MagicMock) -> None:
    patch_get_client.document_types.list.return_value = MagicMock(count=0, results=[])
    list_document_types(name_contains="invoice")
    assert patch_get_client.document_types.list.call_args.kwargs["name_contains"] == "invoice"


def test_list_document_types_passes_name_exact(patch_get_client: MagicMock) -> None:
    patch_get_client.document_types.list.return_value = MagicMock(count=0, results=[])
    list_document_types(name_exact="Invoice")
    assert patch_get_client.document_types.list.call_args.kwargs["name_exact"] == "Invoice"


def test_list_document_types_passes_pagination_params(patch_get_client: MagicMock) -> None:
    patch_get_client.document_types.list.return_value = MagicMock(count=0, results=[])
    list_document_types(page=2, page_size=50, ordering="name", descending=True)
    call_kwargs = patch_get_client.document_types.list.call_args.kwargs
    assert call_kwargs["page"] == 2
    assert call_kwargs["page_size"] == 50
    assert call_kwargs["ordering"] == "name"
    assert call_kwargs["descending"] is True


def test_list_document_types_omits_none_optional_params(patch_get_client: MagicMock) -> None:
    patch_get_client.document_types.list.return_value = MagicMock(count=0, results=[])
    list_document_types()
    call_kwargs = patch_get_client.document_types.list.call_args.kwargs
    assert "ids" not in call_kwargs
    assert "name_contains" not in call_kwargs
    assert "name_exact" not in call_kwargs
    assert "page" not in call_kwargs
    assert "page_size" not in call_kwargs
    assert "ordering" not in call_kwargs


def test_list_document_types_descending_default_is_false(patch_get_client: MagicMock) -> None:
    patch_get_client.document_types.list.return_value = MagicMock(count=0, results=[])
    list_document_types()
    assert patch_get_client.document_types.list.call_args.kwargs["descending"] is False


def test_list_document_types_returns_document_type_objects(patch_get_client: MagicMock) -> None:
    patch_get_client.document_types.list.return_value = MagicMock(count=1, results=[make_document_type(id=5, name="Contract")])
    result = list_document_types()
    assert isinstance(result.items[0], DocumentType)
    assert result.items[0].id == 5
    assert result.items[0].name == "Contract"


# ---------------------------------------------------------------------------
# get_document_type
# ---------------------------------------------------------------------------


def test_get_document_type_calls_client(patch_get_client: MagicMock) -> None:
    patch_get_client.document_types.get.return_value = make_document_type(id=7)
    result = get_document_type(7)
    patch_get_client.document_types.get.assert_called_once_with(id=7)
    assert result.id == 7


def test_get_document_type_returns_document_type(patch_get_client: MagicMock) -> None:
    patch_get_client.document_types.get.return_value = make_document_type(id=3, name="Receipt")
    result = get_document_type(3)
    assert isinstance(result, DocumentType)
    assert result.name == "Receipt"


# ---------------------------------------------------------------------------
# create_document_type
# ---------------------------------------------------------------------------


def test_create_document_type_minimal(patch_get_client: MagicMock) -> None:
    patch_get_client.document_types.create.return_value = make_document_type(id=10, name="Contract")
    result = create_document_type(name="Contract")
    patch_get_client.document_types.create.assert_called_once()
    call_kwargs = patch_get_client.document_types.create.call_args.kwargs
    assert call_kwargs["name"] == "Contract"
    assert result.id == 10


def test_create_document_type_is_insensitive_default_is_true(patch_get_client: MagicMock) -> None:
    patch_get_client.document_types.create.return_value = make_document_type(id=1)
    create_document_type(name="Invoice")
    call_kwargs = patch_get_client.document_types.create.call_args.kwargs
    assert call_kwargs["is_insensitive"] is True


def test_create_document_type_passes_all_params(patch_get_client: MagicMock) -> None:
    patch_get_client.document_types.create.return_value = make_document_type(id=11)
    perms = MagicMock(spec=SetPermissions)
    create_document_type(
        name="Invoice",
        match="invoice",
        matching_algorithm=MatchingAlgorithm.ANY_WORD,
        is_insensitive=False,
        owner=5,
        set_permissions=perms,
    )
    call_kwargs = patch_get_client.document_types.create.call_args.kwargs
    assert call_kwargs["name"] == "Invoice"
    assert call_kwargs["match"] == "invoice"
    assert call_kwargs["matching_algorithm"] == MatchingAlgorithm.ANY_WORD
    assert call_kwargs["is_insensitive"] is False
    assert call_kwargs["owner"] == 5
    assert call_kwargs["set_permissions"] is perms


def test_create_document_type_omits_none_optional_params(patch_get_client: MagicMock) -> None:
    patch_get_client.document_types.create.return_value = make_document_type(id=1)
    create_document_type(name="Minimal")
    call_kwargs = patch_get_client.document_types.create.call_args.kwargs
    assert "match" not in call_kwargs
    assert "matching_algorithm" not in call_kwargs
    assert "owner" not in call_kwargs
    assert "set_permissions" not in call_kwargs


def test_create_document_type_returns_document_type(patch_get_client: MagicMock) -> None:
    patch_get_client.document_types.create.return_value = make_document_type(id=20, name="Created")
    result = create_document_type(name="Created")
    assert isinstance(result, DocumentType)
    assert result.name == "Created"


# ---------------------------------------------------------------------------
# update_document_type
# ---------------------------------------------------------------------------


def test_update_document_type_passes_provided_fields(patch_get_client: MagicMock) -> None:
    patch_get_client.document_types.update.return_value = make_document_type(id=1, name="Renamed")
    update_document_type(1, name="Renamed")
    call_args = patch_get_client.document_types.update.call_args
    assert call_args.args[0] == 1
    assert call_args.kwargs.get("name") == "Renamed"


def test_update_document_type_omits_unset_fields(patch_get_client: MagicMock) -> None:
    """Fields not passed must not be forwarded to the client (UNSET sentinel)."""
    patch_get_client.document_types.update.return_value = make_document_type(id=1)
    update_document_type(1, name="X")
    call_kwargs = patch_get_client.document_types.update.call_args.kwargs
    assert "match" not in call_kwargs
    assert "matching_algorithm" not in call_kwargs
    assert "is_insensitive" not in call_kwargs
    assert "owner" not in call_kwargs
    assert "set_permissions" not in call_kwargs


def test_update_document_type_no_extra_kwargs_when_only_id(patch_get_client: MagicMock) -> None:
    patch_get_client.document_types.update.return_value = make_document_type(id=1)
    update_document_type(1)
    assert patch_get_client.document_types.update.call_args.kwargs == {}


def test_update_document_type_passes_all_params(patch_get_client: MagicMock) -> None:
    patch_get_client.document_types.update.return_value = make_document_type(id=5)
    perms = MagicMock(spec=SetPermissions)
    update_document_type(
        5,
        name="Updated",
        match="updated",
        matching_algorithm=MatchingAlgorithm.EXACT,
        is_insensitive=False,
        owner=7,
        set_permissions=perms,
    )
    call_kwargs = patch_get_client.document_types.update.call_args.kwargs
    assert call_kwargs["name"] == "Updated"
    assert call_kwargs["match"] == "updated"
    assert call_kwargs["matching_algorithm"] == MatchingAlgorithm.EXACT
    assert call_kwargs["is_insensitive"] is False
    assert call_kwargs["owner"] == 7
    assert call_kwargs["set_permissions"] is perms


def test_update_document_type_clears_nullable_fields_when_none_passed(patch_get_client: MagicMock) -> None:
    """Explicitly passing None must forward None to the client (clear the field)."""
    patch_get_client.document_types.update.return_value = make_document_type(id=1)
    update_document_type(1, match=None, owner=None)
    call_kwargs = patch_get_client.document_types.update.call_args.kwargs
    assert "match" in call_kwargs
    assert call_kwargs["match"] is None
    assert "owner" in call_kwargs
    assert call_kwargs["owner"] is None


def test_update_document_type_returns_document_type(patch_get_client: MagicMock) -> None:
    patch_get_client.document_types.update.return_value = make_document_type(id=1, name="Updated")
    result = update_document_type(1, name="Updated")
    assert isinstance(result, DocumentType)


# ---------------------------------------------------------------------------
# delete_document_type
# ---------------------------------------------------------------------------


def test_delete_document_type_calls_client(patch_get_client: MagicMock) -> None:
    delete_document_type(99)
    patch_get_client.document_types.delete.assert_called_once_with(id=99)


def test_delete_document_type_returns_none(patch_get_client: MagicMock) -> None:
    patch_get_client.document_types.delete.return_value = None
    result = delete_document_type(1)
    assert result is None


# ---------------------------------------------------------------------------
# bulk_delete_document_types
# ---------------------------------------------------------------------------


def test_bulk_delete_document_types_calls_client(patch_get_client: MagicMock) -> None:
    bulk_delete_document_types([10, 11, 12])
    patch_get_client.document_types.bulk_delete.assert_called_once_with([10, 11, 12])


def test_bulk_delete_document_types_returns_none(patch_get_client: MagicMock) -> None:
    patch_get_client.document_types.bulk_delete.return_value = None
    result = bulk_delete_document_types([1, 2])
    assert result is None


# ---------------------------------------------------------------------------
# bulk_set_document_type_permissions
# ---------------------------------------------------------------------------


def test_bulk_set_document_type_permissions_calls_client(patch_get_client: MagicMock) -> None:
    bulk_set_document_type_permissions([1, 2, 3], owner=5, merge=True)
    patch_get_client.document_types.bulk_set_permissions.assert_called_once_with(
        [1, 2, 3], set_permissions=None, owner=5, merge=True
    )


def test_bulk_set_document_type_permissions_with_set_permissions(patch_get_client: MagicMock) -> None:
    perms = MagicMock(spec=SetPermissions)
    bulk_set_document_type_permissions([4, 5], set_permissions=perms)
    patch_get_client.document_types.bulk_set_permissions.assert_called_once_with(
        [4, 5], set_permissions=perms, owner=None, merge=False
    )


def test_bulk_set_document_type_permissions_defaults(patch_get_client: MagicMock) -> None:
    bulk_set_document_type_permissions([1])
    call_kwargs = patch_get_client.document_types.bulk_set_permissions.call_args.kwargs
    assert call_kwargs["set_permissions"] is None
    assert call_kwargs["owner"] is None
    assert call_kwargs["merge"] is False


def test_bulk_set_document_type_permissions_returns_none(patch_get_client: MagicMock) -> None:
    patch_get_client.document_types.bulk_set_permissions.return_value = None
    result = bulk_set_document_type_permissions([1])
    assert result is None
