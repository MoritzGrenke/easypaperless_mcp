"""Custom fields sub-server: MCP tools for the paperless-ngx custom fields resource."""

from typing import Any

from easypaperless import UNSET, CustomField, SetPermissions
from fastmcp import FastMCP

from ..client import get_client

# Typed alias so mypy accepts UNSET as a default for any optional param type.
_UNSET: Any = UNSET

custom_fields = FastMCP("custom_fields")


@custom_fields.tool
def list_custom_fields(
    name_contains: str | None = None,
    name_exact: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
    ordering: str | None = None,
    descending: bool = False,
) -> list[CustomField]:
    """List custom fields defined in paperless-ngx with optional filtering.

    Args:
        name_contains: Filter to custom fields whose name contains this string.
        name_exact: Filter to custom fields with this exact name.
        page: Page number for manual pagination.
        page_size: Number of results per page.
        ordering: Field name to sort by (e.g. "name", "-id").
        descending: Reverse the ordering direction. Default: False.

    Returns:
        List of CustomField objects.
    """
    client = get_client()
    kwargs: dict[str, Any] = {}
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
    return client.custom_fields.list(**kwargs).results


@custom_fields.tool
def get_custom_field(id: int) -> CustomField:
    """Fetch a single custom field by its ID.

    Args:
        id: Numeric paperless-ngx custom field ID.

    Returns:
        The CustomField with the given ID.
    """
    client = get_client()
    return client.custom_fields.get(id=id)


@custom_fields.tool
def create_custom_field(
    name: str,
    data_type: str,
    extra_data: dict[str, Any] | None = None,
    owner: int | None = None,
    set_permissions: SetPermissions | None = None,
) -> CustomField:
    """Create a new custom field.

    Args:
        name: Custom field name.
        data_type: Data type of the field. One of: string, boolean, integer,
            float, monetary, date, url, documentlink, select.
        extra_data: Additional configuration data for the field (e.g. select
            options).
        owner: Numeric user ID to assign as custom field owner.
        set_permissions: Explicit view/change permission sets.

    Returns:
        The created CustomField.
    """
    client = get_client()
    kwargs: dict[str, Any] = {
        "name": name,
        "data_type": data_type,
    }
    if extra_data is not None:
        kwargs["extra_data"] = extra_data
    if owner is not None:
        kwargs["owner"] = owner
    if set_permissions is not None:
        kwargs["set_permissions"] = set_permissions
    return client.custom_fields.create(**kwargs)


@custom_fields.tool
def update_custom_field(
    id: int,
    name: str | None = _UNSET,
    data_type: str | None = _UNSET,
    extra_data: dict[str, Any] | None = _UNSET,
    owner: int | None = _UNSET,
    set_permissions: SetPermissions | None = _UNSET,
) -> CustomField:
    """Partially update a custom field (PATCH semantics).

    Only fields explicitly provided are sent to the API. Fields omitted
    are not changed on the server. Pass None for a nullable field to clear it.

    Args:
        id: Numeric ID of the custom field to update.
        name: New custom field name. Omit to leave unchanged.
        data_type: New data type. One of: string, boolean, integer, float,
            monetary, date, url, documentlink, select. Omit to leave unchanged.
        extra_data: Additional configuration data. Omit to leave unchanged,
            or None to clear.
        owner: Numeric user ID to assign as custom field owner. Omit to leave
            unchanged, or None to clear.
        set_permissions: Explicit view/change permission sets. Omit to leave
            unchanged, or None to clear.

    Returns:
        The updated CustomField.
    """
    client = get_client()
    kwargs: dict[str, Any] = {}
    if name is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["name"] = name
    if data_type is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["data_type"] = data_type
    if extra_data is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["extra_data"] = extra_data
    if owner is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["owner"] = owner
    if set_permissions is not UNSET:  # type: ignore[comparison-overlap]
        kwargs["set_permissions"] = set_permissions
    return client.custom_fields.update(id, **kwargs)


@custom_fields.tool
def delete_custom_field(id: int) -> None:
    """Permanently delete a custom field by its ID.

    This action is irreversible. Documents with values for this custom field
    will have those values removed.

    Args:
        id: Numeric ID of the custom field to delete.
    """
    client = get_client()
    client.custom_fields.delete(id=id)
