"""Users sub-server: MCP tools for the paperless-ngx users resource."""

from datetime import datetime
from typing import Any

from easypaperless import UNSET, User
from fastmcp import FastMCP

from ..client import get_client
from .models import ListResult

# Typed alias so mypy accepts UNSET as a default for any optional param type.
_UNSET: Any = UNSET

users = FastMCP("users")


@users.tool
def list_users(
    username_contains: str | None = None,
    username_exact: str | None = None,
    ordering: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
) -> ListResult[User]:
    """List users defined in paperless-ngx with optional filtering.

    Args:
        username_contains: Case-insensitive substring filter on username.
        username_exact: Case-insensitive exact match on username.
        ordering: Field name to sort by (e.g. "username", "-id").
        page: Page number for manual pagination.
        page_size: Number of results per page.

    Returns:
        ListResult with count (total matching users in paperless-ngx) and
        items (list of User objects).
    """
    client = get_client()
    kwargs: dict[str, Any] = {}
    if username_contains is not None:
        kwargs["username_contains"] = username_contains
    if username_exact is not None:
        kwargs["username_exact"] = username_exact
    if ordering is not None:
        kwargs["ordering"] = ordering
    if page is not None:
        kwargs["page"] = page
    if page_size is not None:
        kwargs["page_size"] = page_size
    paged = client.users.list(**kwargs)
    return ListResult(count=paged.count, items=paged.results)


@users.tool
def get_user(id: int) -> User:
    """Fetch a single user by their ID.

    Args:
        id: Numeric paperless-ngx user ID.

    Returns:
        The User with the given ID.

    Raises:
        NotFoundError: If no user exists with that ID.
    """
    client = get_client()
    return client.users.get(id=id)


@users.tool
def create_user(
    username: str,
    email: str | None = None,
    password: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    date_joined: datetime | None = None,
    is_staff: bool | None = None,
    is_active: bool | None = None,
    is_superuser: bool | None = None,
    groups: list[int] | None = None,
    user_permissions: list[str] | None = None,
) -> User:
    """Create a new user account.

    Args:
        username: Login username. Must be unique. Required.
        email: Email address.
        password: Password for the new account.
        first_name: Given name.
        last_name: Family name.
        date_joined: Account creation timestamp.
        is_staff: Grant staff (admin UI) access.
        is_active: Whether the account is active.
        is_superuser: Grant unrestricted superuser access.
        groups: IDs of groups to assign the user to.
        user_permissions: Directly assigned permission strings.

    Returns:
        The newly created User.
    """
    client = get_client()
    kwargs: dict[str, Any] = {"username": username}
    if email is not None:
        kwargs["email"] = email
    if password is not None:
        kwargs["password"] = password
    if first_name is not None:
        kwargs["first_name"] = first_name
    if last_name is not None:
        kwargs["last_name"] = last_name
    if date_joined is not None:
        kwargs["date_joined"] = date_joined
    if is_staff is not None:
        kwargs["is_staff"] = is_staff
    if is_active is not None:
        kwargs["is_active"] = is_active
    if is_superuser is not None:
        kwargs["is_superuser"] = is_superuser
    if groups is not None:
        kwargs["groups"] = groups
    if user_permissions is not None:
        kwargs["user_permissions"] = user_permissions
    return client.users.create(**kwargs)


@users.tool
def update_user(
    id: int,
    username: str | None = _UNSET,
    email: str | None = _UNSET,
    password: str | None = _UNSET,
    first_name: str | None = _UNSET,
    last_name: str | None = _UNSET,
    date_joined: datetime | None = _UNSET,
    is_staff: bool | None = _UNSET,
    is_active: bool | None = _UNSET,
    is_superuser: bool | None = _UNSET,
    groups: list[int] | None = _UNSET,
    user_permissions: list[str] | None = _UNSET,
) -> User:
    """Partially update a user account (PATCH semantics).

    Only fields explicitly provided are sent to the API. Fields omitted
    are not changed on the server. Pass None for a nullable field to clear it.

    Args:
        id: Numeric ID of the user to update.
        username: Login username. Omit to leave unchanged.
        email: Email address. Omit to leave unchanged, or None to clear.
        password: New password. Omit to leave unchanged, or None to clear.
        first_name: Given name. Omit to leave unchanged, or None to clear.
        last_name: Family name. Omit to leave unchanged, or None to clear.
        date_joined: Account creation timestamp. Omit to leave unchanged,
            or None to clear.
        is_staff: Grant or revoke staff access. Omit to leave unchanged,
            or None to clear.
        is_active: Activate or deactivate the account. Omit to leave
            unchanged, or None to clear.
        is_superuser: Grant or revoke superuser access. Omit to leave
            unchanged, or None to clear.
        groups: IDs of groups to assign the user to. Omit to leave
            unchanged, or None to clear.
        user_permissions: Directly assigned permission strings. Omit to
            leave unchanged, or None to clear.

    Returns:
        The updated User.
    """
    client = get_client()
    kwargs: dict[str, Any] = {}
    if username is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["username"] = username
    if email is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["email"] = email
    if password is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["password"] = password
    if first_name is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["first_name"] = first_name
    if last_name is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["last_name"] = last_name
    if date_joined is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["date_joined"] = date_joined
    if is_staff is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["is_staff"] = is_staff
    if is_active is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["is_active"] = is_active
    if is_superuser is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["is_superuser"] = is_superuser
    if groups is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["groups"] = groups
    if user_permissions is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["user_permissions"] = user_permissions
    return client.users.update(id, **kwargs)


@users.tool
def delete_user(id: int) -> None:
    """Permanently delete a user account by their ID.

    This action is irreversible.

    Args:
        id: Numeric ID of the user to delete.

    Raises:
        NotFoundError: If no user exists with that ID.
    """
    client = get_client()
    client.users.delete(id=id)
