"""Tags sub-server: MCP tools for the paperless-ngx tags resource."""

from typing import Any

from easypaperless import UNSET, MatchingAlgorithm, SetPermissions, Tag
from fastmcp import FastMCP

from ..client import get_client

# Typed alias so mypy accepts UNSET as a default for any optional param type.
_UNSET: Any = UNSET

tags = FastMCP("tags")


@tags.tool
def list_tags(
    ids: list[int] | None = None,
    name_contains: str | None = None,
    name_exact: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
    ordering: str | None = None,
    descending: bool = False,
) -> list[Tag]:
    """List tags defined in paperless-ngx with optional filtering.

    Args:
        ids: Restrict results to this specific set of tag IDs.
        name_contains: Filter to tags whose name contains this string.
        name_exact: Filter to tags with this exact name.
        page: Page number for manual pagination.
        page_size: Number of results per page.
        ordering: Field name to sort by (e.g. "name", "-id").
        descending: Reverse the ordering direction. Default: False.

    Returns:
        List of Tag objects.
    """
    client = get_client()
    kwargs: dict[str, Any] = {}
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
    return client.tags.list(**kwargs).results


@tags.tool
def get_tag(id: int) -> Tag:
    """Fetch a single tag by its ID.

    Args:
        id: Numeric paperless-ngx tag ID.

    Returns:
        The Tag with the given ID.
    """
    client = get_client()
    return client.tags.get(id=id)


@tags.tool
def create_tag(
    name: str,
    color: str | None = None,
    is_inbox_tag: bool | None = None,
    match: str | None = None,
    matching_algorithm: MatchingAlgorithm | None = None,
    is_insensitive: bool = True,
    parent: int | None = None,
    owner: int | None = None,
    set_permissions: SetPermissions | None = None,
) -> Tag:
    """Create a new tag.

    Args:
        name: Tag name.
        color: Hex colour code for the tag in the UI (e.g. "#a6cee3").
        is_inbox_tag: When True, newly ingested documents receive this tag automatically.
        match: Text pattern used by the auto-matching rule.
        matching_algorithm: Algorithm to use for auto-matching. One of: NONE, ANY_WORD,
            ALL_WORDS, EXACT, REGEX, FUZZY, AUTO.
        is_insensitive: When True, matching is case-insensitive. Default: True.
        parent: ID of the parent tag for hierarchical tag trees.
        owner: Numeric user ID to assign as tag owner.
        set_permissions: Explicit view/change permission sets.

    Returns:
        The created Tag.
    """
    client = get_client()
    kwargs: dict[str, Any] = {
        "name": name,
        "is_insensitive": is_insensitive,
    }
    if color is not None:
        kwargs["color"] = color
    if is_inbox_tag is not None:
        kwargs["is_inbox_tag"] = is_inbox_tag
    if match is not None:
        kwargs["match"] = match
    if matching_algorithm is not None:
        kwargs["matching_algorithm"] = matching_algorithm
    if parent is not None:
        kwargs["parent"] = parent
    if owner is not None:
        kwargs["owner"] = owner
    if set_permissions is not None:
        kwargs["set_permissions"] = set_permissions
    return client.tags.create(**kwargs)


@tags.tool
def update_tag(
    id: int,
    name: str | None = _UNSET,
    color: str | None = _UNSET,
    is_inbox_tag: bool | None = _UNSET,
    match: str | None = _UNSET,
    matching_algorithm: MatchingAlgorithm | None = _UNSET,
    is_insensitive: bool | None = _UNSET,
    parent: int | None = _UNSET,
    owner: int | None = _UNSET,
    set_permissions: SetPermissions | None = _UNSET,
) -> Tag:
    """Partially update a tag (PATCH semantics).

    Only fields explicitly provided are sent to the API. Fields omitted
    are not changed on the server. Pass None for a nullable field to clear it.

    Args:
        id: Numeric ID of the tag to update.
        name: New tag name. Omit to leave unchanged.
        color: Hex colour code for the tag in the UI. Omit to leave unchanged,
            or None to clear.
        is_inbox_tag: When True, newly ingested documents receive this tag
            automatically. Omit to leave unchanged, or None to clear.
        match: Text pattern used by the auto-matching rule. Omit to leave
            unchanged, or None to clear.
        matching_algorithm: Algorithm to use for auto-matching. One of: NONE,
            ANY_WORD, ALL_WORDS, EXACT, REGEX, FUZZY, AUTO. Omit to leave
            unchanged, or None to clear.
        is_insensitive: When True, matching is case-insensitive. Omit to leave
            unchanged, or None to clear.
        parent: ID of the parent tag for hierarchical tag trees. Omit to leave
            unchanged, or None to clear (remove from parent).
        owner: Numeric user ID to assign as tag owner. Omit to leave unchanged,
            or None to clear.
        set_permissions: Explicit view/change permission sets. Omit to leave
            unchanged, or None to clear.

    Returns:
        The updated Tag.
    """
    client = get_client()
    kwargs: dict[str, Any] = {}
    if name is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["name"] = name
    if color is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["color"] = color
    if is_inbox_tag is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["is_inbox_tag"] = is_inbox_tag
    if match is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["match"] = match
    if matching_algorithm is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["matching_algorithm"] = matching_algorithm
    if is_insensitive is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["is_insensitive"] = is_insensitive
    if parent is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["parent"] = parent
    if owner is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["owner"] = owner
    if set_permissions is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["set_permissions"] = set_permissions
    return client.tags.update(id, **kwargs)


@tags.tool
def delete_tag(id: int) -> None:
    """Permanently delete a tag by its ID.

    This action is irreversible. Documents that had this tag will have it removed.

    Args:
        id: Numeric ID of the tag to delete.
    """
    client = get_client()
    client.tags.delete(id=id)


@tags.tool
def bulk_delete_tags(ids: list[int]) -> None:
    """Permanently delete multiple tags in a single request.

    This action is irreversible.

    Args:
        ids: List of tag IDs to delete.
    """
    client = get_client()
    client.tags.bulk_delete(ids)


@tags.tool
def bulk_set_tag_permissions(
    ids: list[int],
    set_permissions: SetPermissions | None = None,
    owner: int | None = None,
    merge: bool = False,
) -> None:
    """Set permissions and/or owner on multiple tags.

    Args:
        ids: List of tag IDs to modify.
        set_permissions: Explicit view/change permission sets. Contains
            view.users, view.groups, change.users, change.groups lists.
        owner: Numeric user ID to assign as tag owner.
        merge: When True, new permissions are merged with existing ones.
            Default: False (replace).
    """
    client = get_client()
    client.tags.bulk_set_permissions(ids, set_permissions=set_permissions, owner=owner, merge=merge)  # type: ignore[arg-type]
