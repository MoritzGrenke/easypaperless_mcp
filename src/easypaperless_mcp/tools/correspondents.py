"""Correspondents sub-server: MCP tools for the paperless-ngx correspondents resource."""

from typing import Any

from easypaperless import UNSET, Correspondent, MatchingAlgorithm, SetPermissions
from fastmcp import FastMCP

from ..client import get_client

# Typed alias so mypy accepts UNSET as a default for any optional param type.
_UNSET: Any = UNSET

correspondents = FastMCP("correspondents")


@correspondents.tool
def list_correspondents(
    ids: list[int] | None = None,
    name_contains: str | None = None,
    name_exact: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
    ordering: str | None = None,
    descending: bool = False,
) -> list[Correspondent]:
    """List correspondents defined in paperless-ngx with optional filtering.

    Args:
        ids: Restrict results to this specific set of correspondent IDs.
        name_contains: Filter to correspondents whose name contains this string.
        name_exact: Filter to correspondents with this exact name.
        page: Page number for manual pagination.
        page_size: Number of results per page.
        ordering: Field name to sort by (e.g. "name", "-id").
        descending: Reverse the ordering direction. Default: False.

    Returns:
        List of Correspondent objects.
    """
    client = get_client()
    kwargs: dict = {}
    if ids is not None:
        kwargs["ids"] = ids
    if name_contains is not None:
        kwargs["name_contains"] = name_contains
    if name_exact is not None:
        kwargs["name_exact"] = name_exact
    if page is not None:
        kwargs["page"] = page
    if page_size is not None:
        kwargs["page_size"] = page_size
    if ordering is not None:
        kwargs["ordering"] = ordering
    kwargs["descending"] = descending
    return client.correspondents.list(**kwargs)


@correspondents.tool
def get_correspondent(id: int) -> Correspondent:
    """Fetch a single correspondent by its ID.

    Args:
        id: Numeric paperless-ngx correspondent ID.

    Returns:
        The Correspondent with the given ID.
    """
    client = get_client()
    return client.correspondents.get(id=id)


@correspondents.tool
def create_correspondent(
    name: str,
    match: str | None = None,
    matching_algorithm: MatchingAlgorithm | None = None,
    is_insensitive: bool = True,
    owner: int | None = None,
    set_permissions: SetPermissions | None = None,
) -> Correspondent:
    """Create a new correspondent.

    Args:
        name: Correspondent name.
        match: Text pattern used by the auto-matching rule.
        matching_algorithm: Algorithm to use for auto-matching. One of: NONE, ANY_WORD,
            ALL_WORDS, EXACT, REGEX, FUZZY, AUTO.
        is_insensitive: When True, matching is case-insensitive. Default: True.
        owner: Numeric user ID to assign as correspondent owner.
        set_permissions: Explicit view/change permission sets.

    Returns:
        The created Correspondent.
    """
    client = get_client()
    kwargs: dict = {
        "name": name,
        "is_insensitive": is_insensitive,
    }
    if match is not None:
        kwargs["match"] = match
    if matching_algorithm is not None:
        kwargs["matching_algorithm"] = matching_algorithm
    if owner is not None:
        kwargs["owner"] = owner
    if set_permissions is not None:
        kwargs["set_permissions"] = set_permissions
    return client.correspondents.create(**kwargs)


@correspondents.tool
def update_correspondent(
    id: int,
    name: str | None = _UNSET,
    match: str | None = _UNSET,
    matching_algorithm: MatchingAlgorithm | None = _UNSET,
    is_insensitive: bool | None = _UNSET,
    owner: int | None = _UNSET,
    set_permissions: SetPermissions | None = _UNSET,
) -> Correspondent:
    """Partially update a correspondent (PATCH semantics).

    Only fields explicitly provided are sent to the API. Fields omitted
    are not changed on the server. Pass None for a nullable field to clear it.

    Args:
        id: Numeric ID of the correspondent to update.
        name: New correspondent name. Omit to leave unchanged.
        match: Text pattern used by the auto-matching rule. Omit to leave
            unchanged, or None to clear.
        matching_algorithm: Algorithm to use for auto-matching. One of: NONE,
            ANY_WORD, ALL_WORDS, EXACT, REGEX, FUZZY, AUTO. Omit to leave
            unchanged, or None to clear.
        is_insensitive: When True, matching is case-insensitive. Omit to leave
            unchanged, or None to clear.
        owner: Numeric user ID to assign as correspondent owner. Omit to leave
            unchanged, or None to clear.
        set_permissions: Explicit view/change permission sets. Omit to leave
            unchanged, or None to clear.

    Returns:
        The updated Correspondent.
    """
    client = get_client()
    kwargs: dict[str, Any] = {}
    if name is not UNSET:
        kwargs["name"] = name
    if match is not UNSET:
        kwargs["match"] = match
    if matching_algorithm is not UNSET:
        kwargs["matching_algorithm"] = matching_algorithm
    if is_insensitive is not UNSET:
        kwargs["is_insensitive"] = is_insensitive
    if owner is not UNSET:
        kwargs["owner"] = owner
    if set_permissions is not UNSET:
        kwargs["set_permissions"] = set_permissions
    return client.correspondents.update(id, **kwargs)


@correspondents.tool
def delete_correspondent(id: int) -> None:
    """Permanently delete a correspondent by its ID.

    This action is irreversible. Documents assigned to this correspondent
    will have the correspondent field cleared.

    Args:
        id: Numeric ID of the correspondent to delete.
    """
    client = get_client()
    client.correspondents.delete(id=id)


@correspondents.tool
def bulk_delete_correspondents(ids: list[int]) -> None:
    """Permanently delete multiple correspondents in a single request.

    This action is irreversible.

    Args:
        ids: List of correspondent IDs to delete.
    """
    client = get_client()
    client.correspondents.bulk_delete(ids)


@correspondents.tool
def bulk_set_correspondent_permissions(
    ids: list[int],
    set_permissions: SetPermissions | None = None,
    owner: int | None = None,
    merge: bool = False,
) -> None:
    """Set permissions and/or owner on multiple correspondents.

    Args:
        ids: List of correspondent IDs to modify.
        set_permissions: Explicit view/change permission sets. Contains
            view.users, view.groups, change.users, change.groups lists.
        owner: Numeric user ID to assign as correspondent owner.
        merge: When True, new permissions are merged with existing ones.
            Default: False (replace).
    """
    client = get_client()
    client.correspondents.bulk_set_permissions(ids, set_permissions=set_permissions, owner=owner, merge=merge)
