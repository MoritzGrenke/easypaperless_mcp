"""Document types sub-server: MCP tools for the paperless-ngx document types resource."""

from typing import Any

from easypaperless import UNSET, DocumentType, MatchingAlgorithm, SetPermissions
from fastmcp import FastMCP

from ..client import get_client

# Typed alias so mypy accepts UNSET as a default for any optional param type.
_UNSET: Any = UNSET

document_types = FastMCP("document_types")


@document_types.tool
def list_document_types(
    ids: list[int] | None = None,
    name_contains: str | None = None,
    name_exact: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
    ordering: str | None = None,
    descending: bool = False,
) -> list[DocumentType]:
    """List document types defined in paperless-ngx with optional filtering.

    Args:
        ids: Restrict results to this specific set of document type IDs.
        name_contains: Filter to document types whose name contains this string.
        name_exact: Filter to document types with this exact name.
        page: Page number for manual pagination.
        page_size: Number of results per page.
        ordering: Field name to sort by (e.g. "name", "-id").
        descending: Reverse the ordering direction. Default: False.

    Returns:
        List of DocumentType objects.
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
    return client.document_types.list(**kwargs).results


@document_types.tool
def get_document_type(id: int) -> DocumentType:
    """Fetch a single document type by its ID.

    Args:
        id: Numeric paperless-ngx document type ID.

    Returns:
        The DocumentType with the given ID.
    """
    client = get_client()
    return client.document_types.get(id=id)


@document_types.tool
def create_document_type(
    name: str,
    match: str | None = None,
    matching_algorithm: MatchingAlgorithm | None = None,
    is_insensitive: bool = True,
    owner: int | None = None,
    set_permissions: SetPermissions | None = None,
) -> DocumentType:
    """Create a new document type.

    Args:
        name: Document type name.
        match: Text pattern used by the auto-matching rule.
        matching_algorithm: Algorithm to use for auto-matching. One of: NONE, ANY_WORD,
            ALL_WORDS, EXACT, REGEX, FUZZY, AUTO.
        is_insensitive: When True, matching is case-insensitive. Default: True.
        owner: Numeric user ID to assign as document type owner.
        set_permissions: Explicit view/change permission sets.

    Returns:
        The created DocumentType.
    """
    client = get_client()
    kwargs: dict[str, Any] = {
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
    return client.document_types.create(**kwargs)


@document_types.tool
def update_document_type(
    id: int,
    name: str | None = _UNSET,
    match: str | None = _UNSET,
    matching_algorithm: MatchingAlgorithm | None = _UNSET,
    is_insensitive: bool | None = _UNSET,
    owner: int | None = _UNSET,
    set_permissions: SetPermissions | None = _UNSET,
) -> DocumentType:
    """Partially update a document type (PATCH semantics).

    Only fields explicitly provided are sent to the API. Fields omitted
    are not changed on the server. Pass None for a nullable field to clear it.

    Args:
        id: Numeric ID of the document type to update.
        name: New document type name. Omit to leave unchanged.
        match: Text pattern used by the auto-matching rule. Omit to leave
            unchanged, or None to clear.
        matching_algorithm: Algorithm to use for auto-matching. One of: NONE,
            ANY_WORD, ALL_WORDS, EXACT, REGEX, FUZZY, AUTO. Omit to leave
            unchanged, or None to clear.
        is_insensitive: When True, matching is case-insensitive. Omit to leave
            unchanged, or None to clear.
        owner: Numeric user ID to assign as document type owner. Omit to leave
            unchanged, or None to clear.
        set_permissions: Explicit view/change permission sets. Omit to leave
            unchanged, or None to clear.

    Returns:
        The updated DocumentType.
    """
    client = get_client()
    kwargs: dict[str, Any] = {}
    if name is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["name"] = name
    if match is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["match"] = match
    if matching_algorithm is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["matching_algorithm"] = matching_algorithm
    if is_insensitive is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["is_insensitive"] = is_insensitive
    if owner is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["owner"] = owner
    if set_permissions is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["set_permissions"] = set_permissions
    return client.document_types.update(id, **kwargs)


@document_types.tool
def delete_document_type(id: int) -> None:
    """Permanently delete a document type by its ID.

    This action is irreversible. Documents assigned to this type will have
    the document type field cleared.

    Args:
        id: Numeric ID of the document type to delete.
    """
    client = get_client()
    client.document_types.delete(id=id)


@document_types.tool
def bulk_delete_document_types(ids: list[int]) -> None:
    """Permanently delete multiple document types in a single request.

    This action is irreversible.

    Args:
        ids: List of document type IDs to delete.
    """
    client = get_client()
    client.document_types.bulk_delete(ids)


@document_types.tool
def bulk_set_document_type_permissions(
    ids: list[int],
    set_permissions: SetPermissions | None = None,
    owner: int | None = None,
    merge: bool = False,
) -> None:
    """Set permissions and/or owner on multiple document types.

    Args:
        ids: List of document type IDs to modify.
        set_permissions: Explicit view/change permission sets. Contains
            view.users, view.groups, change.users, change.groups lists.
        owner: Numeric user ID to assign as document type owner.
        merge: When True, new permissions are merged with existing ones.
            Default: False (replace).
    """
    client = get_client()
    client.document_types.bulk_set_permissions(ids, set_permissions=set_permissions, owner=owner, merge=merge)  # type: ignore[arg-type]
