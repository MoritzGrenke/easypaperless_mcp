"""Unit tests for storage paths sub-server tools."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from easypaperless import MatchingAlgorithm, SetPermissions, StoragePath

from easypaperless_mcp.tools.storage_paths import (
    bulk_delete_storage_paths,
    bulk_set_storage_path_permissions,
    create_storage_path,
    delete_storage_path,
    get_storage_path,
    list_storage_paths,
    update_storage_path,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def patch_storage_paths_get_client(patch_get_client: MagicMock):
    """Also patch get_client inside the storage_paths module."""
    with patch("easypaperless_mcp.tools.storage_paths.get_client", return_value=patch_get_client):
        yield patch_get_client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_storage_path(**kwargs: Any) -> StoragePath:
    """Build a minimal StoragePath with sensible defaults."""
    defaults: dict[str, Any] = {
        "id": 1,
        "name": "Test Storage Path",
    }
    defaults.update(kwargs)
    return StoragePath.model_validate(defaults)


# ---------------------------------------------------------------------------
# list_storage_paths
# ---------------------------------------------------------------------------


def test_list_storage_paths_calls_client(patch_get_client: MagicMock) -> None:
    patch_get_client.storage_paths.list.return_value = [make_storage_path(id=1), make_storage_path(id=2)]
    result = list_storage_paths()
    patch_get_client.storage_paths.list.assert_called_once()
    assert len(result) == 2


def test_list_storage_paths_returns_empty_list(patch_get_client: MagicMock) -> None:
    patch_get_client.storage_paths.list.return_value = []
    assert list_storage_paths() == []


def test_list_storage_paths_returns_storage_path_objects(patch_get_client: MagicMock) -> None:
    patch_get_client.storage_paths.list.return_value = [make_storage_path(id=5, name="Archive")]
    result = list_storage_paths()
    assert isinstance(result[0], StoragePath)
    assert result[0].id == 5
    assert result[0].name == "Archive"


def test_list_storage_paths_passes_ids(patch_get_client: MagicMock) -> None:
    patch_get_client.storage_paths.list.return_value = []
    list_storage_paths(ids=[1, 2, 3])
    assert patch_get_client.storage_paths.list.call_args.kwargs["ids"] == [1, 2, 3]


def test_list_storage_paths_passes_name_contains(patch_get_client: MagicMock) -> None:
    patch_get_client.storage_paths.list.return_value = []
    list_storage_paths(name_contains="archive")
    assert patch_get_client.storage_paths.list.call_args.kwargs["name_contains"] == "archive"


def test_list_storage_paths_passes_name_exact(patch_get_client: MagicMock) -> None:
    patch_get_client.storage_paths.list.return_value = []
    list_storage_paths(name_exact="Archive")
    assert patch_get_client.storage_paths.list.call_args.kwargs["name_exact"] == "Archive"


def test_list_storage_paths_passes_path_contains(patch_get_client: MagicMock) -> None:
    patch_get_client.storage_paths.list.return_value = []
    list_storage_paths(path_contains="{correspondent}")
    assert patch_get_client.storage_paths.list.call_args.kwargs["path_contains"] == "{correspondent}"


def test_list_storage_paths_passes_path_exact(patch_get_client: MagicMock) -> None:
    patch_get_client.storage_paths.list.return_value = []
    list_storage_paths(path_exact="{correspondent}/{title}")
    assert patch_get_client.storage_paths.list.call_args.kwargs["path_exact"] == "{correspondent}/{title}"


def test_list_storage_paths_passes_pagination_params(patch_get_client: MagicMock) -> None:
    patch_get_client.storage_paths.list.return_value = []
    list_storage_paths(page=2, page_size=50, ordering="name", descending=True)
    call_kwargs = patch_get_client.storage_paths.list.call_args.kwargs
    assert call_kwargs["page"] == 2
    assert call_kwargs["page_size"] == 50
    assert call_kwargs["ordering"] == "name"
    assert call_kwargs["descending"] is True


def test_list_storage_paths_omits_none_optional_params(patch_get_client: MagicMock) -> None:
    patch_get_client.storage_paths.list.return_value = []
    list_storage_paths()
    call_kwargs = patch_get_client.storage_paths.list.call_args.kwargs
    assert "ids" not in call_kwargs
    assert "name_contains" not in call_kwargs
    assert "name_exact" not in call_kwargs
    assert "path_contains" not in call_kwargs
    assert "path_exact" not in call_kwargs
    assert "page" not in call_kwargs
    assert "page_size" not in call_kwargs
    assert "ordering" not in call_kwargs


def test_list_storage_paths_descending_default_is_false(patch_get_client: MagicMock) -> None:
    patch_get_client.storage_paths.list.return_value = []
    list_storage_paths()
    assert patch_get_client.storage_paths.list.call_args.kwargs["descending"] is False


# ---------------------------------------------------------------------------
# get_storage_path
# ---------------------------------------------------------------------------


def test_get_storage_path_calls_client(patch_get_client: MagicMock) -> None:
    patch_get_client.storage_paths.get.return_value = make_storage_path(id=7)
    result = get_storage_path(7)
    patch_get_client.storage_paths.get.assert_called_once_with(id=7)
    assert result.id == 7


def test_get_storage_path_returns_storage_path(patch_get_client: MagicMock) -> None:
    patch_get_client.storage_paths.get.return_value = make_storage_path(id=3, name="Receipts")
    result = get_storage_path(3)
    assert isinstance(result, StoragePath)
    assert result.name == "Receipts"


# ---------------------------------------------------------------------------
# create_storage_path
# ---------------------------------------------------------------------------


def test_create_storage_path_minimal(patch_get_client: MagicMock) -> None:
    patch_get_client.storage_paths.create.return_value = make_storage_path(id=10, name="New Path")
    result = create_storage_path(name="New Path", path="{title}")
    patch_get_client.storage_paths.create.assert_called_once()
    call_kwargs = patch_get_client.storage_paths.create.call_args.kwargs
    assert call_kwargs["name"] == "New Path"
    assert call_kwargs["path"] == "{title}"
    assert result.id == 10


def test_create_storage_path_is_insensitive_default_is_true(patch_get_client: MagicMock) -> None:
    patch_get_client.storage_paths.create.return_value = make_storage_path(id=1)
    create_storage_path(name="Test", path="{title}")
    call_kwargs = patch_get_client.storage_paths.create.call_args.kwargs
    assert call_kwargs["is_insensitive"] is True


def test_create_storage_path_passes_all_params(patch_get_client: MagicMock) -> None:
    patch_get_client.storage_paths.create.return_value = make_storage_path(id=11)
    perms = MagicMock(spec=SetPermissions)
    create_storage_path(
        name="Invoice Archive",
        path="{correspondent}/{title}",
        match="invoice",
        matching_algorithm=MatchingAlgorithm.ANY_WORD,
        is_insensitive=False,
        owner=5,
        set_permissions=perms,
    )
    call_kwargs = patch_get_client.storage_paths.create.call_args.kwargs
    assert call_kwargs["name"] == "Invoice Archive"
    assert call_kwargs["path"] == "{correspondent}/{title}"
    assert call_kwargs["match"] == "invoice"
    assert call_kwargs["matching_algorithm"] == MatchingAlgorithm.ANY_WORD
    assert call_kwargs["is_insensitive"] is False
    assert call_kwargs["owner"] == 5
    assert call_kwargs["set_permissions"] is perms


def test_create_storage_path_omits_none_optional_params(patch_get_client: MagicMock) -> None:
    patch_get_client.storage_paths.create.return_value = make_storage_path(id=1)
    create_storage_path(name="Minimal", path="{title}")
    call_kwargs = patch_get_client.storage_paths.create.call_args.kwargs
    assert "match" not in call_kwargs
    assert "matching_algorithm" not in call_kwargs
    assert "owner" not in call_kwargs
    assert "set_permissions" not in call_kwargs


def test_create_storage_path_returns_storage_path(patch_get_client: MagicMock) -> None:
    patch_get_client.storage_paths.create.return_value = make_storage_path(id=20, name="Created")
    result = create_storage_path(name="Created", path="{title}")
    assert isinstance(result, StoragePath)
    assert result.name == "Created"


# ---------------------------------------------------------------------------
# update_storage_path
# ---------------------------------------------------------------------------


def test_update_storage_path_passes_provided_fields(patch_get_client: MagicMock) -> None:
    patch_get_client.storage_paths.update.return_value = make_storage_path(id=1, name="Renamed")
    update_storage_path(1, name="Renamed")
    call_args = patch_get_client.storage_paths.update.call_args
    assert call_args.args[0] == 1
    assert call_args.kwargs.get("name") == "Renamed"


def test_update_storage_path_omits_unset_fields(patch_get_client: MagicMock) -> None:
    """Fields not passed must not be forwarded to the client (UNSET sentinel)."""
    patch_get_client.storage_paths.update.return_value = make_storage_path(id=1)
    update_storage_path(1, name="X")
    call_kwargs = patch_get_client.storage_paths.update.call_args.kwargs
    assert "path" not in call_kwargs
    assert "match" not in call_kwargs
    assert "matching_algorithm" not in call_kwargs
    assert "is_insensitive" not in call_kwargs
    assert "owner" not in call_kwargs
    assert "set_permissions" not in call_kwargs


def test_update_storage_path_no_extra_kwargs_when_only_id(patch_get_client: MagicMock) -> None:
    patch_get_client.storage_paths.update.return_value = make_storage_path(id=1)
    update_storage_path(1)
    assert patch_get_client.storage_paths.update.call_args.kwargs == {}


def test_update_storage_path_passes_all_params(patch_get_client: MagicMock) -> None:
    patch_get_client.storage_paths.update.return_value = make_storage_path(id=5)
    perms = MagicMock(spec=SetPermissions)
    update_storage_path(
        5,
        name="Updated",
        path="{title}",
        match="updated",
        matching_algorithm=MatchingAlgorithm.EXACT,
        is_insensitive=False,
        owner=7,
        set_permissions=perms,
    )
    call_kwargs = patch_get_client.storage_paths.update.call_args.kwargs
    assert call_kwargs["name"] == "Updated"
    assert call_kwargs["path"] == "{title}"
    assert call_kwargs["match"] == "updated"
    assert call_kwargs["matching_algorithm"] == MatchingAlgorithm.EXACT
    assert call_kwargs["is_insensitive"] is False
    assert call_kwargs["owner"] == 7
    assert call_kwargs["set_permissions"] is perms


def test_update_storage_path_clears_nullable_fields_when_none_passed(patch_get_client: MagicMock) -> None:
    """Explicitly passing None must forward None to the client (clear the field)."""
    patch_get_client.storage_paths.update.return_value = make_storage_path(id=1)
    update_storage_path(1, path=None, match=None, owner=None)
    call_kwargs = patch_get_client.storage_paths.update.call_args.kwargs
    assert "path" in call_kwargs
    assert call_kwargs["path"] is None
    assert "match" in call_kwargs
    assert call_kwargs["match"] is None
    assert "owner" in call_kwargs
    assert call_kwargs["owner"] is None


def test_update_storage_path_returns_storage_path(patch_get_client: MagicMock) -> None:
    patch_get_client.storage_paths.update.return_value = make_storage_path(id=1, name="Updated")
    result = update_storage_path(1, name="Updated")
    assert isinstance(result, StoragePath)


# ---------------------------------------------------------------------------
# delete_storage_path
# ---------------------------------------------------------------------------


def test_delete_storage_path_calls_client(patch_get_client: MagicMock) -> None:
    delete_storage_path(99)
    patch_get_client.storage_paths.delete.assert_called_once_with(id=99)


def test_delete_storage_path_returns_none(patch_get_client: MagicMock) -> None:
    patch_get_client.storage_paths.delete.return_value = None
    result = delete_storage_path(1)
    assert result is None


# ---------------------------------------------------------------------------
# bulk_delete_storage_paths
# ---------------------------------------------------------------------------


def test_bulk_delete_storage_paths_calls_client(patch_get_client: MagicMock) -> None:
    bulk_delete_storage_paths([10, 11, 12])
    patch_get_client.storage_paths.bulk_delete.assert_called_once_with([10, 11, 12])


def test_bulk_delete_storage_paths_returns_none(patch_get_client: MagicMock) -> None:
    patch_get_client.storage_paths.bulk_delete.return_value = None
    result = bulk_delete_storage_paths([1, 2])
    assert result is None


def test_bulk_delete_storage_paths_empty_list(patch_get_client: MagicMock) -> None:
    bulk_delete_storage_paths([])
    patch_get_client.storage_paths.bulk_delete.assert_called_once_with([])


# ---------------------------------------------------------------------------
# bulk_set_storage_path_permissions
# ---------------------------------------------------------------------------


def test_bulk_set_storage_path_permissions_calls_client(patch_get_client: MagicMock) -> None:
    bulk_set_storage_path_permissions([1, 2, 3], owner=5, merge=True)
    patch_get_client.storage_paths.bulk_set_permissions.assert_called_once_with(
        [1, 2, 3], set_permissions=None, owner=5, merge=True
    )


def test_bulk_set_storage_path_permissions_with_set_permissions(patch_get_client: MagicMock) -> None:
    perms = MagicMock(spec=SetPermissions)
    bulk_set_storage_path_permissions([4, 5], set_permissions=perms)
    patch_get_client.storage_paths.bulk_set_permissions.assert_called_once_with(
        [4, 5], set_permissions=perms, owner=None, merge=False
    )


def test_bulk_set_storage_path_permissions_defaults(patch_get_client: MagicMock) -> None:
    bulk_set_storage_path_permissions([1])
    call_kwargs = patch_get_client.storage_paths.bulk_set_permissions.call_args.kwargs
    assert call_kwargs["set_permissions"] is None
    assert call_kwargs["owner"] is None
    assert call_kwargs["merge"] is False


def test_bulk_set_storage_path_permissions_returns_none(patch_get_client: MagicMock) -> None:
    patch_get_client.storage_paths.bulk_set_permissions.return_value = None
    result = bulk_set_storage_path_permissions([1])
    assert result is None
