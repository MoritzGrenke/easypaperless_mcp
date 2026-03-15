"""Storage paths sub-server: MCP tools for the paperless-ngx storage paths resource."""

from typing import Any

from easypaperless import UNSET, MatchingAlgorithm, SetPermissions, StoragePath
from fastmcp import FastMCP

from ..client import get_client

# Typed alias so mypy accepts UNSET as a default for any optional param type.
_UNSET: Any = UNSET

storage_paths = FastMCP("storage_paths")


@storage_paths.tool
def list_storage_paths(
    ids: list[int] | None = None,
    name_contains: str | None = None,
    name_exact: str | None = None,
    path_contains: str | None = None,
    path_exact: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
    ordering: str | None = None,
    descending: bool = False,
) -> list[StoragePath]:
    """List storage paths defined in paperless-ngx with optional filtering.

    Args:
        ids: Restrict results to this specific set of storage path IDs.
        name_contains: Filter to storage paths whose name contains this string.
        name_exact: Filter to storage paths with this exact name.
        path_contains: Filter to storage paths whose path template contains this string.
        path_exact: Filter to storage paths with this exact path template.
        page: Page number for manual pagination.
        page_size: Number of results per page.
        ordering: Field name to sort by (e.g. "name", "-id").
        descending: Reverse the ordering direction. Default: False.

    Returns:
        List of StoragePath objects.
    """
    client = get_client()
    kwargs: dict = {}
    if ids is not None:
        kwargs["ids"] = ids
    if name_contains is not None:
        kwargs["name_contains"] = name_contains
    if name_exact is not None:
        kwargs["name_exact"] = name_exact
    if path_contains is not None:
        kwargs["path_contains"] = path_contains
    if path_exact is not None:
        kwargs["path_exact"] = path_exact
    if page is not None:
        kwargs["page"] = page
    if page_size is not None:
        kwargs["page_size"] = page_size
    if ordering is not None:
        kwargs["ordering"] = ordering
    kwargs["descending"] = descending
    return client.storage_paths.list(**kwargs)


@storage_paths.tool
def get_storage_path(id: int) -> StoragePath:
    """Fetch a single storage path by its ID.

    Args:
        id: Numeric paperless-ngx storage path ID.

    Returns:
        The StoragePath with the given ID.
    """
    client = get_client()
    return client.storage_paths.get(id=id)


@storage_paths.tool
def create_storage_path(
    name: str,
    path: str,
    match: str | None = None,
    matching_algorithm: MatchingAlgorithm | None = None,
    is_insensitive: bool = True,
    owner: int | None = None,
    set_permissions: SetPermissions | None = None,
) -> StoragePath:
    """Create a new storage path.

    Args:
        name: Storage path name.
        path: Archive file path template (e.g. "{correspondent}/{title}"). Required by paperless-ngx.
        match: Text pattern used by the auto-matching rule.
        matching_algorithm: Algorithm to use for auto-matching. One of: NONE, ANY_WORD,
            ALL_WORDS, EXACT, REGEX, FUZZY, AUTO.
        is_insensitive: When True, matching is case-insensitive. Default: True.
        owner: Numeric user ID to assign as storage path owner.
        set_permissions: Explicit view/change permission sets.

    Returns:
        The created StoragePath.
    """
    client = get_client()
    kwargs: dict = {
        "name": name,
        "path": path,
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
    return client.storage_paths.create(**kwargs)


@storage_paths.tool
def update_storage_path(
    id: int,
    name: str | None = _UNSET,
    path: str | None = _UNSET,
    match: str | None = _UNSET,
    matching_algorithm: MatchingAlgorithm | None = _UNSET,
    is_insensitive: bool | None = _UNSET,
    owner: int | None = _UNSET,
    set_permissions: SetPermissions | None = _UNSET,
) -> StoragePath:
    """Partially update a storage path (PATCH semantics).

    Only fields explicitly provided are sent to the API. Fields omitted
    are not changed on the server. Pass None for a nullable field to clear it.

    Args:
        id: Numeric ID of the storage path to update.
        name: New storage path name. Omit to leave unchanged.
        path: Archive file path template. Omit to leave unchanged, or None to clear.
        match: Text pattern used by the auto-matching rule. Omit to leave
            unchanged, or None to clear.
        matching_algorithm: Algorithm to use for auto-matching. One of: NONE,
            ANY_WORD, ALL_WORDS, EXACT, REGEX, FUZZY, AUTO. Omit to leave
            unchanged, or None to clear.
        is_insensitive: When True, matching is case-insensitive. Omit to leave
            unchanged, or None to clear.
        owner: Numeric user ID to assign as storage path owner. Omit to leave
            unchanged, or None to clear.
        set_permissions: Explicit view/change permission sets. Omit to leave
            unchanged, or None to clear.

    Returns:
        The updated StoragePath.
    """
    client = get_client()
    kwargs: dict[str, Any] = {}
    if name is not UNSET:
        kwargs["name"] = name
    if path is not UNSET:
        kwargs["path"] = path
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
    return client.storage_paths.update(id, **kwargs)


@storage_paths.tool
def delete_storage_path(id: int) -> None:
    """Permanently delete a storage path by its ID.

    This action is irreversible. Documents assigned to this storage path will
    have the storage path field cleared.

    Args:
        id: Numeric ID of the storage path to delete.
    """
    client = get_client()
    client.storage_paths.delete(id=id)


@storage_paths.tool
def bulk_delete_storage_paths(ids: list[int]) -> None:
    """Permanently delete multiple storage paths in a single request.

    This action is irreversible.

    Args:
        ids: List of storage path IDs to delete.
    """
    client = get_client()
    client.storage_paths.bulk_delete(ids)


@storage_paths.tool
def bulk_set_storage_path_permissions(
    ids: list[int],
    set_permissions: SetPermissions | None = None,
    owner: int | None = None,
    merge: bool = False,
) -> None:
    """Set permissions and/or owner on multiple storage paths.

    Args:
        ids: List of storage path IDs to modify.
        set_permissions: Explicit view/change permission sets. Contains
            view.users, view.groups, change.users, change.groups lists.
        owner: Numeric user ID to assign as storage path owner.
        merge: When True, new permissions are merged with existing ones.
            Default: False (replace).
    """
    client = get_client()
    client.storage_paths.bulk_set_permissions(ids, set_permissions=set_permissions, owner=owner, merge=merge)
