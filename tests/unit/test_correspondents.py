"""Unit tests for correspondents sub-server tools."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from easypaperless import Correspondent, MatchingAlgorithm, SetPermissions

from easypaperless_mcp.tools.correspondents import (
    bulk_delete_correspondents,
    bulk_set_correspondent_permissions,
    create_correspondent,
    delete_correspondent,
    get_correspondent,
    list_correspondents,
    update_correspondent,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def patch_correspondents_get_client(patch_get_client: MagicMock):
    """Also patch get_client inside the correspondents module."""
    with patch("easypaperless_mcp.tools.correspondents.get_client", return_value=patch_get_client):
        yield patch_get_client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_correspondent(**kwargs: Any) -> Correspondent:
    """Build a minimal Correspondent with sensible defaults."""
    defaults: dict[str, Any] = {
        "id": 1,
        "name": "Test Correspondent",
    }
    defaults.update(kwargs)
    return Correspondent.model_validate(defaults)


# ---------------------------------------------------------------------------
# list_correspondents
# ---------------------------------------------------------------------------


def test_list_correspondents_calls_client(patch_get_client: MagicMock) -> None:
    patch_get_client.correspondents.list.return_value = MagicMock(count=2, results=[make_correspondent(id=1), make_correspondent(id=2)])
    result = list_correspondents()
    patch_get_client.correspondents.list.assert_called_once()
    assert result.count == 2
    assert len(result.items) == 2


def test_list_correspondents_returns_empty_list(patch_get_client: MagicMock) -> None:
    patch_get_client.correspondents.list.return_value = MagicMock(count=0, results=[])
    result = list_correspondents()
    assert result.count == 0
    assert result.items == []


def test_list_correspondents_passes_ids(patch_get_client: MagicMock) -> None:
    patch_get_client.correspondents.list.return_value = MagicMock(count=0, results=[])
    list_correspondents(ids=[1, 2, 3])
    assert patch_get_client.correspondents.list.call_args.kwargs["ids"] == [1, 2, 3]


def test_list_correspondents_passes_name_contains(patch_get_client: MagicMock) -> None:
    patch_get_client.correspondents.list.return_value = MagicMock(count=0, results=[])
    list_correspondents(name_contains="acme")
    assert patch_get_client.correspondents.list.call_args.kwargs["name_contains"] == "acme"


def test_list_correspondents_passes_name_exact(patch_get_client: MagicMock) -> None:
    patch_get_client.correspondents.list.return_value = MagicMock(count=0, results=[])
    list_correspondents(name_exact="ACME Corp")
    assert patch_get_client.correspondents.list.call_args.kwargs["name_exact"] == "ACME Corp"


def test_list_correspondents_passes_pagination_params(patch_get_client: MagicMock) -> None:
    patch_get_client.correspondents.list.return_value = MagicMock(count=0, results=[])
    list_correspondents(page=2, page_size=50, ordering="name", descending=True)
    call_kwargs = patch_get_client.correspondents.list.call_args.kwargs
    assert call_kwargs["page"] == 2
    assert call_kwargs["page_size"] == 50
    assert call_kwargs["ordering"] == "name"
    assert call_kwargs["descending"] is True


def test_list_correspondents_omits_none_optional_params(patch_get_client: MagicMock) -> None:
    patch_get_client.correspondents.list.return_value = MagicMock(count=0, results=[])
    list_correspondents()
    call_kwargs = patch_get_client.correspondents.list.call_args.kwargs
    assert "ids" not in call_kwargs
    assert "name_contains" not in call_kwargs
    assert "name_exact" not in call_kwargs
    assert "page" not in call_kwargs
    assert "ordering" not in call_kwargs


def test_list_correspondents_returns_correspondent_objects(patch_get_client: MagicMock) -> None:
    patch_get_client.correspondents.list.return_value = MagicMock(count=1, results=[make_correspondent(id=5, name="Bank")])
    result = list_correspondents()
    assert isinstance(result.items[0], Correspondent)
    assert result.items[0].id == 5
    assert result.items[0].name == "Bank"


# ---------------------------------------------------------------------------
# get_correspondent
# ---------------------------------------------------------------------------


def test_get_correspondent_calls_client(patch_get_client: MagicMock) -> None:
    patch_get_client.correspondents.get.return_value = make_correspondent(id=7)
    result = get_correspondent(7)
    patch_get_client.correspondents.get.assert_called_once_with(id=7)
    assert result.id == 7


def test_get_correspondent_returns_correspondent(patch_get_client: MagicMock) -> None:
    patch_get_client.correspondents.get.return_value = make_correspondent(id=3, name="Landlord")
    result = get_correspondent(3)
    assert isinstance(result, Correspondent)
    assert result.name == "Landlord"


# ---------------------------------------------------------------------------
# create_correspondent
# ---------------------------------------------------------------------------


def test_create_correspondent_minimal(patch_get_client: MagicMock) -> None:
    patch_get_client.correspondents.create.return_value = make_correspondent(id=10, name="New Corp")
    result = create_correspondent(name="New Corp")
    patch_get_client.correspondents.create.assert_called_once()
    call_kwargs = patch_get_client.correspondents.create.call_args.kwargs
    assert call_kwargs["name"] == "New Corp"
    assert result.id == 10


def test_create_correspondent_passes_all_params(patch_get_client: MagicMock) -> None:
    patch_get_client.correspondents.create.return_value = make_correspondent(id=11)
    perms = MagicMock(spec=SetPermissions)
    create_correspondent(
        name="ACME",
        match="acme",
        matching_algorithm=MatchingAlgorithm.ANY_WORD,
        is_insensitive=True,
        owner=5,
        set_permissions=perms,
    )
    call_kwargs = patch_get_client.correspondents.create.call_args.kwargs
    assert call_kwargs["name"] == "ACME"
    assert call_kwargs["match"] == "acme"
    assert call_kwargs["matching_algorithm"] == MatchingAlgorithm.ANY_WORD
    assert call_kwargs["is_insensitive"] is True
    assert call_kwargs["owner"] == 5
    assert call_kwargs["set_permissions"] is perms


def test_create_correspondent_omits_none_optional_params(patch_get_client: MagicMock) -> None:
    patch_get_client.correspondents.create.return_value = make_correspondent(id=1)
    create_correspondent(name="Minimal")
    call_kwargs = patch_get_client.correspondents.create.call_args.kwargs
    assert "match" not in call_kwargs
    assert "matching_algorithm" not in call_kwargs
    assert "owner" not in call_kwargs
    assert "set_permissions" not in call_kwargs


def test_create_correspondent_returns_correspondent(patch_get_client: MagicMock) -> None:
    patch_get_client.correspondents.create.return_value = make_correspondent(id=20, name="Created")
    result = create_correspondent(name="Created")
    assert isinstance(result, Correspondent)
    assert result.name == "Created"


# ---------------------------------------------------------------------------
# update_correspondent
# ---------------------------------------------------------------------------


def test_update_correspondent_passes_provided_fields(patch_get_client: MagicMock) -> None:
    patch_get_client.correspondents.update.return_value = make_correspondent(id=1, name="Renamed")
    update_correspondent(1, name="Renamed")
    call_args = patch_get_client.correspondents.update.call_args
    assert call_args.args[0] == 1
    assert call_args.kwargs.get("name") == "Renamed"


def test_update_correspondent_omits_unset_fields(patch_get_client: MagicMock) -> None:
    """Fields not passed to update_correspondent must not be forwarded to the client."""
    patch_get_client.correspondents.update.return_value = make_correspondent(id=1)
    update_correspondent(1, name="X")
    call_kwargs = patch_get_client.correspondents.update.call_args.kwargs
    assert "match" not in call_kwargs
    assert "matching_algorithm" not in call_kwargs
    assert "is_insensitive" not in call_kwargs
    assert "owner" not in call_kwargs
    assert "set_permissions" not in call_kwargs


def test_update_correspondent_no_extra_kwargs_when_only_id(patch_get_client: MagicMock) -> None:
    patch_get_client.correspondents.update.return_value = make_correspondent(id=1)
    update_correspondent(1)
    assert patch_get_client.correspondents.update.call_args.kwargs == {}


def test_update_correspondent_passes_all_params(patch_get_client: MagicMock) -> None:
    patch_get_client.correspondents.update.return_value = make_correspondent(id=5)
    perms = MagicMock(spec=SetPermissions)
    update_correspondent(
        5,
        name="Updated",
        match="updated",
        matching_algorithm=MatchingAlgorithm.EXACT,
        is_insensitive=False,
        owner=7,
        set_permissions=perms,
    )
    call_kwargs = patch_get_client.correspondents.update.call_args.kwargs
    assert call_kwargs["name"] == "Updated"
    assert call_kwargs["match"] == "updated"
    assert call_kwargs["matching_algorithm"] == MatchingAlgorithm.EXACT
    assert call_kwargs["is_insensitive"] is False
    assert call_kwargs["owner"] == 7
    assert call_kwargs["set_permissions"] is perms


def test_update_correspondent_returns_correspondent(patch_get_client: MagicMock) -> None:
    patch_get_client.correspondents.update.return_value = make_correspondent(id=1, name="Updated")
    result = update_correspondent(1, name="Updated")
    assert isinstance(result, Correspondent)


def test_update_correspondent_clears_nullable_fields_when_none_passed(patch_get_client: MagicMock) -> None:
    """Explicitly passing None must forward None to the client (clear the field)."""
    patch_get_client.correspondents.update.return_value = make_correspondent(id=1)
    update_correspondent(1, match=None, owner=None)
    call_kwargs = patch_get_client.correspondents.update.call_args.kwargs
    assert "match" in call_kwargs
    assert call_kwargs["match"] is None
    assert "owner" in call_kwargs
    assert call_kwargs["owner"] is None


# ---------------------------------------------------------------------------
# delete_correspondent
# ---------------------------------------------------------------------------


def test_delete_correspondent_calls_client(patch_get_client: MagicMock) -> None:
    delete_correspondent(99)
    patch_get_client.correspondents.delete.assert_called_once_with(id=99)


def test_delete_correspondent_returns_none(patch_get_client: MagicMock) -> None:
    patch_get_client.correspondents.delete.return_value = None
    result = delete_correspondent(1)
    assert result is None


# ---------------------------------------------------------------------------
# bulk_delete_correspondents
# ---------------------------------------------------------------------------


def test_bulk_delete_correspondents_calls_client(patch_get_client: MagicMock) -> None:
    bulk_delete_correspondents([10, 11, 12])
    patch_get_client.correspondents.bulk_delete.assert_called_once_with([10, 11, 12])


def test_bulk_delete_correspondents_returns_none(patch_get_client: MagicMock) -> None:
    patch_get_client.correspondents.bulk_delete.return_value = None
    result = bulk_delete_correspondents([1, 2])
    assert result is None


# ---------------------------------------------------------------------------
# bulk_set_correspondent_permissions
# ---------------------------------------------------------------------------


def test_bulk_set_correspondent_permissions_calls_client(patch_get_client: MagicMock) -> None:
    bulk_set_correspondent_permissions([1, 2, 3], owner=5, merge=True)
    patch_get_client.correspondents.bulk_set_permissions.assert_called_once_with(
        [1, 2, 3], set_permissions=None, owner=5, merge=True
    )


def test_bulk_set_correspondent_permissions_with_set_permissions(patch_get_client: MagicMock) -> None:
    perms = MagicMock(spec=SetPermissions)
    bulk_set_correspondent_permissions([4, 5], set_permissions=perms)
    patch_get_client.correspondents.bulk_set_permissions.assert_called_once_with(
        [4, 5], set_permissions=perms, owner=None, merge=False
    )


def test_bulk_set_correspondent_permissions_defaults(patch_get_client: MagicMock) -> None:
    bulk_set_correspondent_permissions([1])
    call_kwargs = patch_get_client.correspondents.bulk_set_permissions.call_args.kwargs
    assert call_kwargs["set_permissions"] is None
    assert call_kwargs["owner"] is None
    assert call_kwargs["merge"] is False


def test_bulk_set_correspondent_permissions_returns_none(patch_get_client: MagicMock) -> None:
    patch_get_client.correspondents.bulk_set_permissions.return_value = None
    result = bulk_set_correspondent_permissions([1])
    assert result is None
