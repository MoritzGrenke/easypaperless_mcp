"""Unit tests for tags sub-server tools."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from easypaperless import MatchingAlgorithm, SetPermissions, Tag

from easypaperless_mcp.tools.tags import (
    bulk_delete_tags,
    bulk_set_tag_permissions,
    create_tag,
    delete_tag,
    get_tag,
    list_tags,
    update_tag,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def patch_tags_get_client(patch_get_client: MagicMock):
    """Also patch get_client inside the tags module."""
    with patch("easypaperless_mcp.tools.tags.get_client", return_value=patch_get_client):
        yield patch_get_client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_tag(**kwargs: Any) -> Tag:
    """Build a minimal Tag with sensible defaults."""
    defaults: dict[str, Any] = {
        "id": 1,
        "name": "Test Tag",
    }
    defaults.update(kwargs)
    return Tag.model_validate(defaults)


# ---------------------------------------------------------------------------
# list_tags
# ---------------------------------------------------------------------------


def test_list_tags_calls_client(patch_get_client: MagicMock) -> None:
    patch_get_client.tags.list.return_value = [make_tag(id=1), make_tag(id=2)]
    result = list_tags()
    patch_get_client.tags.list.assert_called_once()
    assert len(result) == 2


def test_list_tags_returns_empty_list(patch_get_client: MagicMock) -> None:
    patch_get_client.tags.list.return_value = []
    assert list_tags() == []


def test_list_tags_passes_ids(patch_get_client: MagicMock) -> None:
    patch_get_client.tags.list.return_value = []
    list_tags(ids=[1, 2, 3])
    assert patch_get_client.tags.list.call_args.kwargs["ids"] == [1, 2, 3]


def test_list_tags_passes_name_contains(patch_get_client: MagicMock) -> None:
    patch_get_client.tags.list.return_value = []
    list_tags(name_contains="invoice")
    assert patch_get_client.tags.list.call_args.kwargs["name_contains"] == "invoice"


def test_list_tags_passes_name_exact(patch_get_client: MagicMock) -> None:
    patch_get_client.tags.list.return_value = []
    list_tags(name_exact="Invoice")
    assert patch_get_client.tags.list.call_args.kwargs["name_exact"] == "Invoice"


def test_list_tags_passes_pagination_params(patch_get_client: MagicMock) -> None:
    patch_get_client.tags.list.return_value = []
    list_tags(page=2, page_size=50, ordering="name", descending=True)
    call_kwargs = patch_get_client.tags.list.call_args.kwargs
    assert call_kwargs["page"] == 2
    assert call_kwargs["page_size"] == 50
    assert call_kwargs["ordering"] == "name"
    assert call_kwargs["descending"] is True


def test_list_tags_omits_none_optional_params(patch_get_client: MagicMock) -> None:
    patch_get_client.tags.list.return_value = []
    list_tags()
    call_kwargs = patch_get_client.tags.list.call_args.kwargs
    assert "ids" not in call_kwargs
    assert "name_contains" not in call_kwargs
    assert "name_exact" not in call_kwargs
    assert "page" not in call_kwargs
    assert "ordering" not in call_kwargs


def test_list_tags_returns_tag_objects(patch_get_client: MagicMock) -> None:
    patch_get_client.tags.list.return_value = [make_tag(id=5, name="Finance")]
    result = list_tags()
    assert isinstance(result[0], Tag)
    assert result[0].id == 5
    assert result[0].name == "Finance"


# ---------------------------------------------------------------------------
# get_tag
# ---------------------------------------------------------------------------


def test_get_tag_calls_client(patch_get_client: MagicMock) -> None:
    patch_get_client.tags.get.return_value = make_tag(id=7)
    result = get_tag(7)
    patch_get_client.tags.get.assert_called_once_with(id=7)
    assert result.id == 7


def test_get_tag_returns_tag(patch_get_client: MagicMock) -> None:
    patch_get_client.tags.get.return_value = make_tag(id=3, name="Inbox")
    result = get_tag(3)
    assert isinstance(result, Tag)
    assert result.name == "Inbox"


# ---------------------------------------------------------------------------
# create_tag
# ---------------------------------------------------------------------------


def test_create_tag_minimal(patch_get_client: MagicMock) -> None:
    patch_get_client.tags.create.return_value = make_tag(id=10, name="New Tag")
    result = create_tag(name="New Tag")
    patch_get_client.tags.create.assert_called_once()
    call_kwargs = patch_get_client.tags.create.call_args.kwargs
    assert call_kwargs["name"] == "New Tag"
    assert result.id == 10


def test_create_tag_passes_all_params(patch_get_client: MagicMock) -> None:
    patch_get_client.tags.create.return_value = make_tag(id=11)
    perms = MagicMock(spec=SetPermissions)
    create_tag(
        name="Finance",
        color="#FF0000",
        is_inbox_tag=True,
        match="invoice",
        matching_algorithm=MatchingAlgorithm.ANY_WORD,
        is_insensitive=True,
        parent=2,
        owner=5,
        set_permissions=perms,
    )
    call_kwargs = patch_get_client.tags.create.call_args.kwargs
    assert call_kwargs["name"] == "Finance"
    assert call_kwargs["color"] == "#FF0000"
    assert call_kwargs["is_inbox_tag"] is True
    assert call_kwargs["match"] == "invoice"
    assert call_kwargs["matching_algorithm"] == MatchingAlgorithm.ANY_WORD
    assert call_kwargs["is_insensitive"] is True
    assert call_kwargs["parent"] == 2
    assert call_kwargs["owner"] == 5
    assert call_kwargs["set_permissions"] is perms


def test_create_tag_omits_none_optional_params(patch_get_client: MagicMock) -> None:
    patch_get_client.tags.create.return_value = make_tag(id=1)
    create_tag(name="Minimal")
    call_kwargs = patch_get_client.tags.create.call_args.kwargs
    assert "color" not in call_kwargs
    assert "is_inbox_tag" not in call_kwargs
    assert "match" not in call_kwargs
    assert "matching_algorithm" not in call_kwargs
    assert "parent" not in call_kwargs
    assert "owner" not in call_kwargs
    assert "set_permissions" not in call_kwargs


def test_create_tag_returns_tag(patch_get_client: MagicMock) -> None:
    patch_get_client.tags.create.return_value = make_tag(id=20, name="Created")
    result = create_tag(name="Created")
    assert isinstance(result, Tag)
    assert result.name == "Created"


# ---------------------------------------------------------------------------
# update_tag
# ---------------------------------------------------------------------------


def test_update_tag_passes_provided_fields(patch_get_client: MagicMock) -> None:
    patch_get_client.tags.update.return_value = make_tag(id=1, name="Renamed")
    update_tag(1, name="Renamed")
    call_args = patch_get_client.tags.update.call_args
    assert call_args.args[0] == 1
    assert call_args.kwargs.get("name") == "Renamed"


def test_update_tag_omits_unprovided_fields(patch_get_client: MagicMock) -> None:
    """Fields not passed to update_tag must not be forwarded to the client."""
    patch_get_client.tags.update.return_value = make_tag(id=1)
    update_tag(1, name="X")
    call_kwargs = patch_get_client.tags.update.call_args.kwargs
    assert "color" not in call_kwargs
    assert "is_inbox_tag" not in call_kwargs
    assert "match" not in call_kwargs
    assert "parent" not in call_kwargs


def test_update_tag_no_extra_kwargs_when_only_id(patch_get_client: MagicMock) -> None:
    patch_get_client.tags.update.return_value = make_tag(id=1)
    update_tag(1)
    assert patch_get_client.tags.update.call_args.kwargs == {}


def test_update_tag_passes_all_params(patch_get_client: MagicMock) -> None:
    patch_get_client.tags.update.return_value = make_tag(id=5)
    perms = MagicMock(spec=SetPermissions)
    update_tag(
        5,
        name="Updated",
        color="#00FF00",
        is_inbox_tag=False,
        match="receipt",
        matching_algorithm=MatchingAlgorithm.EXACT,
        is_insensitive=False,
        parent=3,
        owner=7,
        set_permissions=perms,
    )
    call_kwargs = patch_get_client.tags.update.call_args.kwargs
    assert call_kwargs["name"] == "Updated"
    assert call_kwargs["color"] == "#00FF00"
    assert call_kwargs["is_inbox_tag"] is False
    assert call_kwargs["match"] == "receipt"
    assert call_kwargs["matching_algorithm"] == MatchingAlgorithm.EXACT
    assert call_kwargs["is_insensitive"] is False
    assert call_kwargs["parent"] == 3
    assert call_kwargs["owner"] == 7
    assert call_kwargs["set_permissions"] is perms


def test_update_tag_returns_tag(patch_get_client: MagicMock) -> None:
    patch_get_client.tags.update.return_value = make_tag(id=1, name="Updated")
    result = update_tag(1, name="Updated")
    assert isinstance(result, Tag)


def test_update_tag_clears_nullable_fields_when_none_passed(patch_get_client: MagicMock) -> None:
    """Explicitly passing None must forward None to the client (clear the field)."""
    patch_get_client.tags.update.return_value = make_tag(id=1)
    update_tag(1, parent=None, owner=None, match=None)
    call_kwargs = patch_get_client.tags.update.call_args.kwargs
    assert "parent" in call_kwargs
    assert call_kwargs["parent"] is None
    assert "owner" in call_kwargs
    assert call_kwargs["owner"] is None
    assert "match" in call_kwargs
    assert call_kwargs["match"] is None


# ---------------------------------------------------------------------------
# delete_tag
# ---------------------------------------------------------------------------


def test_delete_tag_calls_client(patch_get_client: MagicMock) -> None:
    delete_tag(99)
    patch_get_client.tags.delete.assert_called_once_with(id=99)


def test_delete_tag_returns_none(patch_get_client: MagicMock) -> None:
    patch_get_client.tags.delete.return_value = None
    result = delete_tag(1)
    assert result is None


# ---------------------------------------------------------------------------
# bulk_delete_tags
# ---------------------------------------------------------------------------


def test_bulk_delete_tags_calls_client(patch_get_client: MagicMock) -> None:
    bulk_delete_tags([10, 11, 12])
    patch_get_client.tags.bulk_delete.assert_called_once_with([10, 11, 12])


def test_bulk_delete_tags_returns_none(patch_get_client: MagicMock) -> None:
    patch_get_client.tags.bulk_delete.return_value = None
    result = bulk_delete_tags([1, 2])
    assert result is None


# ---------------------------------------------------------------------------
# bulk_set_tag_permissions
# ---------------------------------------------------------------------------


def test_bulk_set_tag_permissions_calls_client(patch_get_client: MagicMock) -> None:
    bulk_set_tag_permissions([1, 2, 3], owner=5, merge=True)
    patch_get_client.tags.bulk_set_permissions.assert_called_once_with(
        [1, 2, 3], set_permissions=None, owner=5, merge=True
    )


def test_bulk_set_tag_permissions_with_set_permissions(patch_get_client: MagicMock) -> None:
    perms = MagicMock(spec=SetPermissions)
    bulk_set_tag_permissions([4, 5], set_permissions=perms)
    patch_get_client.tags.bulk_set_permissions.assert_called_once_with(
        [4, 5], set_permissions=perms, owner=None, merge=False
    )


def test_bulk_set_tag_permissions_defaults(patch_get_client: MagicMock) -> None:
    bulk_set_tag_permissions([1])
    call_kwargs = patch_get_client.tags.bulk_set_permissions.call_args.kwargs
    assert call_kwargs["set_permissions"] is None
    assert call_kwargs["owner"] is None
    assert call_kwargs["merge"] is False


def test_bulk_set_tag_permissions_returns_none(patch_get_client: MagicMock) -> None:
    patch_get_client.tags.bulk_set_permissions.return_value = None
    result = bulk_set_tag_permissions([1])
    assert result is None
