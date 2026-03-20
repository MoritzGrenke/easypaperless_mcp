"""Unit tests for users sub-server tools."""

from datetime import datetime, timezone
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from easypaperless import User

from easypaperless_mcp.tools.users import (
    create_user,
    delete_user,
    get_user,
    list_users,
    update_user,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def patch_users_get_client(patch_get_client: MagicMock):
    """Also patch get_client inside the users module."""
    with patch("easypaperless_mcp.tools.users.get_client", return_value=patch_get_client):
        yield patch_get_client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_user(**kwargs: Any) -> User:
    """Build a minimal User with sensible defaults."""
    defaults: dict[str, Any] = {
        "id": 1,
        "username": "testuser",
    }
    defaults.update(kwargs)
    return User.model_validate(defaults)


# ---------------------------------------------------------------------------
# list_users
# ---------------------------------------------------------------------------


def test_list_users_calls_client(patch_get_client: MagicMock) -> None:
    patch_get_client.users.list.return_value = MagicMock(count=2, results=[make_user(id=1), make_user(id=2)])
    result = list_users()
    patch_get_client.users.list.assert_called_once()
    assert result.count == 2
    assert len(result.items) == 2


def test_list_users_returns_empty_list(patch_get_client: MagicMock) -> None:
    patch_get_client.users.list.return_value = MagicMock(count=0, results=[])
    result = list_users()
    assert result.count == 0
    assert result.items == []


def test_list_users_passes_username_contains(patch_get_client: MagicMock) -> None:
    patch_get_client.users.list.return_value = MagicMock(count=0, results=[])
    list_users(username_contains="admin")
    assert patch_get_client.users.list.call_args.kwargs["username_contains"] == "admin"


def test_list_users_passes_username_exact(patch_get_client: MagicMock) -> None:
    patch_get_client.users.list.return_value = MagicMock(count=0, results=[])
    list_users(username_exact="admin")
    assert patch_get_client.users.list.call_args.kwargs["username_exact"] == "admin"


def test_list_users_passes_pagination_params(patch_get_client: MagicMock) -> None:
    patch_get_client.users.list.return_value = MagicMock(count=0, results=[])
    list_users(page=2, page_size=50, ordering="username")
    call_kwargs = patch_get_client.users.list.call_args.kwargs
    assert call_kwargs["page"] == 2
    assert call_kwargs["page_size"] == 50
    assert call_kwargs["ordering"] == "username"


def test_list_users_omits_none_optional_params(patch_get_client: MagicMock) -> None:
    patch_get_client.users.list.return_value = MagicMock(count=0, results=[])
    list_users()
    call_kwargs = patch_get_client.users.list.call_args.kwargs
    assert "username_contains" not in call_kwargs
    assert "username_exact" not in call_kwargs
    assert "ordering" not in call_kwargs
    assert "page" not in call_kwargs
    assert "page_size" not in call_kwargs


def test_list_users_returns_user_objects(patch_get_client: MagicMock) -> None:
    patch_get_client.users.list.return_value = MagicMock(count=1, results=[make_user(id=5, username="alice")])
    result = list_users()
    assert isinstance(result.items[0], User)
    assert result.items[0].id == 5
    assert result.items[0].username == "alice"


# ---------------------------------------------------------------------------
# get_user
# ---------------------------------------------------------------------------


def test_get_user_calls_client(patch_get_client: MagicMock) -> None:
    patch_get_client.users.get.return_value = make_user(id=7)
    result = get_user(7)
    patch_get_client.users.get.assert_called_once_with(id=7)
    assert result.id == 7


def test_get_user_returns_user(patch_get_client: MagicMock) -> None:
    patch_get_client.users.get.return_value = make_user(id=3, username="bob")
    result = get_user(3)
    assert isinstance(result, User)
    assert result.username == "bob"


def test_get_user_propagates_not_found(patch_get_client: MagicMock) -> None:
    from easypaperless import NotFoundError

    patch_get_client.users.get.side_effect = NotFoundError("User not found")
    with pytest.raises(NotFoundError):
        get_user(9999)


# ---------------------------------------------------------------------------
# create_user
# ---------------------------------------------------------------------------


def test_create_user_minimal(patch_get_client: MagicMock) -> None:
    patch_get_client.users.create.return_value = make_user(id=10, username="newuser")
    result = create_user(username="newuser")
    patch_get_client.users.create.assert_called_once()
    call_kwargs = patch_get_client.users.create.call_args.kwargs
    assert call_kwargs["username"] == "newuser"
    assert result.id == 10


def test_create_user_passes_all_params(patch_get_client: MagicMock) -> None:
    patch_get_client.users.create.return_value = make_user(id=11)
    dt = datetime(2024, 1, 1, tzinfo=timezone.utc)
    create_user(
        username="alice",
        email="alice@example.com",
        password="s3cr3t",
        first_name="Alice",
        last_name="Smith",
        date_joined=dt,
        is_staff=True,
        is_active=True,
        is_superuser=False,
        groups=[1, 2],
        user_permissions=["view_document"],
    )
    call_kwargs = patch_get_client.users.create.call_args.kwargs
    assert call_kwargs["username"] == "alice"
    assert call_kwargs["email"] == "alice@example.com"
    assert call_kwargs["password"] == "s3cr3t"
    assert call_kwargs["first_name"] == "Alice"
    assert call_kwargs["last_name"] == "Smith"
    assert call_kwargs["date_joined"] == dt
    assert call_kwargs["is_staff"] is True
    assert call_kwargs["is_active"] is True
    assert call_kwargs["is_superuser"] is False
    assert call_kwargs["groups"] == [1, 2]
    assert call_kwargs["user_permissions"] == ["view_document"]


def test_create_user_omits_none_optional_params(patch_get_client: MagicMock) -> None:
    patch_get_client.users.create.return_value = make_user(id=1)
    create_user(username="minimal")
    call_kwargs = patch_get_client.users.create.call_args.kwargs
    assert "email" not in call_kwargs
    assert "password" not in call_kwargs
    assert "first_name" not in call_kwargs
    assert "last_name" not in call_kwargs
    assert "date_joined" not in call_kwargs
    assert "is_staff" not in call_kwargs
    assert "is_active" not in call_kwargs
    assert "is_superuser" not in call_kwargs
    assert "groups" not in call_kwargs
    assert "user_permissions" not in call_kwargs


def test_create_user_returns_user(patch_get_client: MagicMock) -> None:
    patch_get_client.users.create.return_value = make_user(id=20, username="created")
    result = create_user(username="created")
    assert isinstance(result, User)
    assert result.username == "created"


# ---------------------------------------------------------------------------
# update_user
# ---------------------------------------------------------------------------


def test_update_user_passes_provided_fields(patch_get_client: MagicMock) -> None:
    patch_get_client.users.update.return_value = make_user(id=1, username="renamed")
    update_user(1, username="renamed")
    call_args = patch_get_client.users.update.call_args
    assert call_args.args[0] == 1
    assert call_args.kwargs.get("username") == "renamed"


def test_update_user_omits_unprovided_fields(patch_get_client: MagicMock) -> None:
    patch_get_client.users.update.return_value = make_user(id=1)
    update_user(1, username="X")
    call_kwargs = patch_get_client.users.update.call_args.kwargs
    assert "email" not in call_kwargs
    assert "password" not in call_kwargs
    assert "first_name" not in call_kwargs
    assert "is_staff" not in call_kwargs
    assert "groups" not in call_kwargs


def test_update_user_no_extra_kwargs_when_only_id(patch_get_client: MagicMock) -> None:
    patch_get_client.users.update.return_value = make_user(id=1)
    update_user(1)
    assert patch_get_client.users.update.call_args.kwargs == {}


def test_update_user_passes_all_params(patch_get_client: MagicMock) -> None:
    patch_get_client.users.update.return_value = make_user(id=5)
    dt = datetime(2024, 6, 15, tzinfo=timezone.utc)
    update_user(
        5,
        username="updated",
        email="updated@example.com",
        password="newpass",
        first_name="Updated",
        last_name="User",
        date_joined=dt,
        is_staff=False,
        is_active=True,
        is_superuser=False,
        groups=[3],
        user_permissions=["add_document"],
    )
    call_kwargs = patch_get_client.users.update.call_args.kwargs
    assert call_kwargs["username"] == "updated"
    assert call_kwargs["email"] == "updated@example.com"
    assert call_kwargs["password"] == "newpass"
    assert call_kwargs["first_name"] == "Updated"
    assert call_kwargs["last_name"] == "User"
    assert call_kwargs["date_joined"] == dt
    assert call_kwargs["is_staff"] is False
    assert call_kwargs["is_active"] is True
    assert call_kwargs["is_superuser"] is False
    assert call_kwargs["groups"] == [3]
    assert call_kwargs["user_permissions"] == ["add_document"]


def test_update_user_returns_user(patch_get_client: MagicMock) -> None:
    patch_get_client.users.update.return_value = make_user(id=1, username="updated")
    result = update_user(1, username="updated")
    assert isinstance(result, User)


def test_update_user_clears_nullable_fields_when_none_passed(patch_get_client: MagicMock) -> None:
    """Explicitly passing None must forward None to the client (clear the field)."""
    patch_get_client.users.update.return_value = make_user(id=1)
    update_user(1, email=None, first_name=None, groups=None)
    call_kwargs = patch_get_client.users.update.call_args.kwargs
    assert "email" in call_kwargs
    assert call_kwargs["email"] is None
    assert "first_name" in call_kwargs
    assert call_kwargs["first_name"] is None
    assert "groups" in call_kwargs
    assert call_kwargs["groups"] is None


# ---------------------------------------------------------------------------
# delete_user
# ---------------------------------------------------------------------------


def test_delete_user_calls_client(patch_get_client: MagicMock) -> None:
    delete_user(99)
    patch_get_client.users.delete.assert_called_once_with(id=99)


def test_delete_user_returns_none(patch_get_client: MagicMock) -> None:
    patch_get_client.users.delete.return_value = None
    result = delete_user(1)
    assert result is None


def test_delete_user_propagates_not_found(patch_get_client: MagicMock) -> None:
    from easypaperless import NotFoundError

    patch_get_client.users.delete.side_effect = NotFoundError("User not found")
    with pytest.raises(NotFoundError):
        delete_user(9999)
