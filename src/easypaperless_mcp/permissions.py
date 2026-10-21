"""Permission-based tool filtering for easypaperless-mcp.

Maps every registered MCP tool to the Django permission it requires.
Provides helpers to resolve a user's effective permissions and filter the
tool list accordingly.

This is a **convenience / UX feature**, not a security boundary. The
authoritative enforcement always remains with paperless-ngx's own API layer.
"""

from collections.abc import Sequence
from typing import Protocol, TypeVar

from easypaperless.models.users import User


class _NamedTool(Protocol):
    """Minimal protocol: any object with a ``name`` attribute."""

    name: str


_T = TypeVar("_T", bound=_NamedTool)


# Maps every registered MCP tool name to the required Django permission string.
# Convention:
#   list_*, get_*, download_*  →  view
#   create_*, upload_*         →  add
#   update_*, bulk_set_*,
#   bulk_add_*, bulk_remove_*,
#   bulk_modify_*              →  change
#   delete_*, bulk_delete_*    →  delete
#
# Sub-resource and non-standard tools use explicit entries.
TOOL_PERMISSIONS: dict[str, str] = {
    # --- Documents ---
    "list_documents": "documents.view_document",
    "get_document": "documents.view_document",
    "get_document_metadata": "documents.view_document",
    "update_document": "documents.change_document",
    "delete_document": "documents.delete_document",
    "upload_document": "documents.add_document",
    "bulk_add_tag": "documents.change_document",
    "bulk_remove_tag": "documents.change_document",
    "bulk_modify_tags": "documents.change_document",
    "bulk_delete_documents": "documents.delete_document",
    "bulk_set_correspondent": "documents.change_document",
    "bulk_set_document_type": "documents.change_document",
    "bulk_set_storage_path": "documents.change_document",
    "bulk_modify_custom_fields": "documents.change_document",
    "bulk_set_permissions": "documents.change_document",
    # --- Document history (auditlog sub-resource) ---
    "get_document_history": "auditlog.view_logentry",
    # --- Document notes (sub-resource) ---
    "list_document_notes": "documents.view_note",
    "create_document_note": "documents.add_note",
    "delete_document_note": "documents.delete_note",
    # --- Tags ---
    "list_tags": "documents.view_tag",
    "get_tag": "documents.view_tag",
    "create_tag": "documents.add_tag",
    "update_tag": "documents.change_tag",
    "delete_tag": "documents.delete_tag",
    "bulk_delete_tags": "documents.delete_tag",
    "bulk_set_tag_permissions": "documents.change_tag",
    # --- Correspondents ---
    "list_correspondents": "documents.view_correspondent",
    "get_correspondent": "documents.view_correspondent",
    "create_correspondent": "documents.add_correspondent",
    "update_correspondent": "documents.change_correspondent",
    "delete_correspondent": "documents.delete_correspondent",
    "bulk_delete_correspondents": "documents.delete_correspondent",
    "bulk_set_correspondent_permissions": "documents.change_correspondent",
    # --- Document types ---
    "list_document_types": "documents.view_documenttype",
    "get_document_type": "documents.view_documenttype",
    "create_document_type": "documents.add_documenttype",
    "update_document_type": "documents.change_documenttype",
    "delete_document_type": "documents.delete_documenttype",
    "bulk_delete_document_types": "documents.delete_documenttype",
    "bulk_set_document_type_permissions": "documents.change_documenttype",
    # --- Custom fields ---
    "list_custom_fields": "documents.view_customfield",
    "get_custom_field": "documents.view_customfield",
    "create_custom_field": "documents.add_customfield",
    "update_custom_field": "documents.change_customfield",
    "delete_custom_field": "documents.delete_customfield",
    # --- Storage paths ---
    "list_storage_paths": "documents.view_storagepath",
    "get_storage_path": "documents.view_storagepath",
    "create_storage_path": "documents.add_storagepath",
    "update_storage_path": "documents.change_storagepath",
    "delete_storage_path": "documents.delete_storagepath",
    "bulk_delete_storage_paths": "documents.delete_storagepath",
    "bulk_set_storage_path_permissions": "documents.change_storagepath",
    # --- Users ---
    "list_users": "auth.view_user",
    "get_user": "auth.view_user",
    "create_user": "auth.add_user",
    "update_user": "auth.change_user",
    "delete_user": "auth.delete_user",
    # --- Trash ---
    "list_trash": "documents.view_document",
    "restore_trash": "documents.change_document",
    "empty_trash": "documents.delete_document",
}


def get_effective_permissions(user: User) -> set[str]:
    """Return the effective permission set for a user.

    Combines ``user_permissions`` (directly assigned) and
    ``inherited_permissions`` (resolved from groups by paperless-ngx).

    Args:
        user: The resolved paperless-ngx user object.

    Returns:
        Set of Django permission strings (e.g. ``"documents.view_document"``).
    """
    perms: set[str] = set()
    if user.user_permissions:
        perms.update(user.user_permissions)
    if user.inherited_permissions:
        perms.update(user.inherited_permissions)
    return perms


def filter_tools_by_permissions(
    tools: Sequence[_T],
    permissions: set[str],
) -> list[_T]:
    """Return only the tools whose required permission is in ``permissions``.

    Tools whose name is absent from :data:`TOOL_PERMISSIONS` are always
    included (fail-open for unknown tools).

    Args:
        tools: Sequence of FastMCP Tool objects (must have a ``name`` attribute).
        permissions: Set of Django permission strings the user holds.

    Returns:
        Filtered list of tools the user is permitted to use.
    """
    return [
        t
        for t in tools
        if TOOL_PERMISSIONS.get(t.name) is None or TOOL_PERMISSIONS[t.name] in permissions
    ]
