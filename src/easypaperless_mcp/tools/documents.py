"""Documents sub-server: MCP tools for the paperless-ngx documents resource."""

from typing import Any

from easypaperless import UNSET, Document, DocumentMetadata, DocumentNote, SetPermissions
from fastmcp import FastMCP
from pydantic.fields import PydanticUndefined

from ..client import get_client

# Typed alias so mypy accepts UNSET as a default for any optional param type.
_UNSET: Any = UNSET

documents = FastMCP("documents")

_LIST_RETURN_FIELDS: list[str] = [
    "id",
    "title",
    "created",
    "correspondent",
    "document_type",
    "tags",
    "archive_serial_number",
]

_GET_RETURN_FIELDS: list[str] = [
    "id",
    "title",
    "created",
    "correspondent",
    "document_type",
    "storage_path",
    "tags",
    "custom_fields",
    "notes",
    "archive_serial_number",
    "original_file_name",
    "page_count",
]


def _filter_fields(doc: Document, return_fields: list[str]) -> Document:
    """Return a copy of doc with all fields not in return_fields set to their type-appropriate empty value.

    Fields are set to their ``default_factory`` result (e.g. ``[]`` for list
    fields), their ``default`` value, or ``None`` for Optional fields — in that
    priority order. Required fields with no default are set to ``None`` as a
    last resort (they should always be included in ``return_fields``).

    Args:
        doc: The document to filter.
        return_fields: Field names to preserve; all others are emptied.

    Returns:
        A model_copy of the document with non-listed fields emptied.
    """
    all_fields = set(doc.__class__.model_fields)
    to_update: dict[str, Any] = {}
    for f in all_fields:
        if f in return_fields:
            continue
        field_info = doc.__class__.model_fields[f]
        if field_info.default_factory is not None:
            to_update[f] = field_info.default_factory()
        elif field_info.default is not PydanticUndefined:
            to_update[f] = field_info.default
        else:
            to_update[f] = None
    if not to_update:
        return doc
    return doc.model_copy(update=to_update)


# ---------------------------------------------------------------------------
# Individual document tools
# ---------------------------------------------------------------------------


@documents.tool
def list_documents(
    search: str | None = None,
    search_mode: str = "title_or_content",
    # ID filtering
    ids: list[int] | None = None,
    # Tag filtering
    tags: list[str] | None = None,
    any_tags: list[int | str] | None = None,
    exclude_tags: list[int | str] | None = None,
    # Correspondent filtering
    correspondent: int | str | None = None,
    any_correspondent: list[int | str] | None = None,
    exclude_correspondents: list[int | str] | None = None,
    # Document type filtering
    document_type: int | str | None = None,
    document_type_name_contains: str | None = None,
    document_type_name_exact: str | None = None,
    any_document_type: list[int | str] | None = None,
    exclude_document_types: list[int | str] | None = None,
    # Storage path filtering
    storage_path: int | str | None = None,
    any_storage_paths: list[int | str] | None = None,
    exclude_storage_paths: list[int | str] | None = None,
    # Owner filtering
    owner: int | None = None,
    exclude_owners: list[int] | None = None,
    # Custom field filtering
    custom_fields: list[int | str] | None = None,
    any_custom_fields: list[int | str] | None = None,
    exclude_custom_fields: list[int | str] | None = None,
    custom_field_query: list[Any] | None = None,
    # Date filtering
    created_after: str | None = None,
    created_before: str | None = None,
    added_after: str | None = None,
    added_from: str | None = None,
    added_before: str | None = None,
    added_until: str | None = None,
    modified_after: str | None = None,
    modified_from: str | None = None,
    modified_before: str | None = None,
    modified_until: str | None = None,
    # Archive serial number filtering
    archive_serial_number: int | None = None,
    archive_serial_number_from: int | None = None,
    archive_serial_number_till: int | None = None,
    # File checksum
    checksum: str | None = None,
    # Ordering & pagination
    ordering: str | None = None,
    page: int | None = None,
    page_size: int = 25,
    descending: bool = False,
    max_results: int = 10,
    return_fields: list[str] | None = ["id", "title", "created", "search_hit"],
) -> list[Document]:
    """List documents from paperless-ngx with optional filtering.

    Only the fields listed in return_fields are populated; all others are set
    to None before returning, keeping token usage low.

    Args:
        search: Search string applied according to search_mode.
        search_mode: How search is applied. One of: 
            "title_or_content" (default), "title", "original_filename",
            "query" - complex search Whoosh query. Supports: phrases "foo bar", wildcards appl*/appl?, 
            boolean AND OR NOT (uppercase), field search title:word. Default operator: AND. 
            searches in title, content, notes, custom_fields, and more fields
        ids: Restrict results to this specific set of document IDs.
        tags: Filter to documents that have ALL of these tags (IDs or names).
        any_tags: Filter to documents that have ANY of these tags (IDs or names).
        exclude_tags: Exclude documents that have ANY of these tags (IDs or names).
        correspondent: Filter to documents with this correspondent (ID or name).
        any_correspondent: Filter to documents with any of these correspondents (IDs or names).
        exclude_correspondents: Exclude documents matching these correspondents (IDs or names).
        document_type: Filter to documents of this type (ID or name).
        document_type_name_contains: Filter by document type name containing this string.
        document_type_name_exact: Filter by exact document type name match.
        any_document_type: Filter to documents of any of these types (IDs or names).
        exclude_document_types: Exclude documents of these types (IDs or names).
        storage_path: Filter to documents in this storage path (ID or name).
        any_storage_paths: Filter to documents in any of these storage paths (IDs or names).
        exclude_storage_paths: Exclude documents in these storage paths (IDs or names).
        owner: Filter to documents owned by this user ID.
        exclude_owners: Exclude documents owned by these user IDs.
        custom_fields: Filter to documents with ALL of these custom fields set (IDs or names).
        any_custom_fields: Filter to documents with ANY of these custom fields set (IDs or names).
        exclude_custom_fields: Exclude documents with ANY of these custom fields set (IDs or names).
        custom_field_query: Filter by custom field values using JSON arrays: ["field_name", "operator", value].
            Operators: exact, in, isnull, exists (all types) | icontains, istartswith, iendswith (text/URL) 
            | gt, gte, lt, lte, range (numbers/dates) | contains (doc links).
            Use ["AND", [[...], [...]]] or ["OR", [[...], [...]]] to combine multiple conditions; 
            nesting is supported. Examples: ["due","range",["2024-08-01","2024-09-01"]] 
            | ["customer","exact","bob"] | ["refs","contains",[3,7]]
        created_after: ISO date string — only documents created after this date.
        created_before: ISO date string — only documents created before this date.
        added_after: ISO datetime string — only documents added after this datetime (exclusive).
        added_from: ISO datetime string — only documents added on or after this datetime (inclusive).
        added_before: ISO datetime string — only documents added before this datetime (exclusive).
        added_until: ISO datetime string — only documents added on or before this datetime (inclusive).
        modified_after: ISO datetime string — only documents modified after this datetime (exclusive).
        modified_from: ISO datetime string — only documents modified on or after this datetime (inclusive).
        modified_before: ISO datetime string — only documents modified before this datetime (exclusive).
        modified_until: ISO datetime string — only documents modified on or before this datetime (inclusive).
        archive_serial_number: Exact ASN match.
        archive_serial_number_from: ASN range start (inclusive).
        archive_serial_number_till: ASN range end (inclusive).
        checksum: Find document by exact file checksum.
        ordering: Field name to sort by (e.g. "created", "-added").
        page: Page number for manual pagination.
        page_size: Number of results per page. Default: 25.
        descending: Reverse the ordering direction. Default: False.
        max_results: Maximum number of documents to return. Default: 10.
        return_fields: Document fields to include in the response. All others
            are set to None. Defaults to the compact summary set ["id", "title", "created", "search_hit"].
            Set to None if you want to receive the full set.

    Returns:
        List of Document objects with only return_fields populated.
    """
    if return_fields is None:
        return_fields = _LIST_RETURN_FIELDS
    client = get_client()
    kwargs: dict[str, Any] = {"max_results": max_results, "page_size": page_size, "descending": descending}
    if search is not None:
        kwargs["search"] = search
        kwargs["search_mode"] = search_mode
    if ids is not None:
        kwargs["ids"] = ids
    if tags is not None:
        kwargs["tags"] = tags
    if any_tags is not None:
        kwargs["any_tags"] = any_tags
    if exclude_tags is not None:
        kwargs["exclude_tags"] = exclude_tags
    if correspondent is not None:
        kwargs["correspondent"] = correspondent
    if any_correspondent is not None:
        kwargs["any_correspondent"] = any_correspondent
    if exclude_correspondents is not None:
        kwargs["exclude_correspondents"] = exclude_correspondents
    if document_type is not None:
        kwargs["document_type"] = document_type
    if document_type_name_contains is not None:
        kwargs["document_type_name_contains"] = document_type_name_contains
    if document_type_name_exact is not None:
        kwargs["document_type_name_exact"] = document_type_name_exact
    if any_document_type is not None:
        kwargs["any_document_type"] = any_document_type
    if exclude_document_types is not None:
        kwargs["exclude_document_types"] = exclude_document_types
    if storage_path is not None:
        kwargs["storage_path"] = storage_path
    if any_storage_paths is not None:
        kwargs["any_storage_paths"] = any_storage_paths
    if exclude_storage_paths is not None:
        kwargs["exclude_storage_paths"] = exclude_storage_paths
    if owner is not None:
        kwargs["owner"] = owner
    if exclude_owners is not None:
        kwargs["exclude_owners"] = exclude_owners
    if custom_fields is not None:
        kwargs["custom_fields"] = custom_fields
    if any_custom_fields is not None:
        kwargs["any_custom_fields"] = any_custom_fields
    if exclude_custom_fields is not None:
        kwargs["exclude_custom_fields"] = exclude_custom_fields
    if custom_field_query is not None:
        kwargs["custom_field_query"] = custom_field_query
    if created_after is not None:
        kwargs["created_after"] = created_after
    if created_before is not None:
        kwargs["created_before"] = created_before
    if added_after is not None:
        kwargs["added_after"] = added_after
    if added_from is not None:
        kwargs["added_from"] = added_from
    if added_before is not None:
        kwargs["added_before"] = added_before
    if added_until is not None:
        kwargs["added_until"] = added_until
    if modified_after is not None:
        kwargs["modified_after"] = modified_after
    if modified_from is not None:
        kwargs["modified_from"] = modified_from
    if modified_before is not None:
        kwargs["modified_before"] = modified_before
    if modified_until is not None:
        kwargs["modified_until"] = modified_until
    if archive_serial_number is not None:
        kwargs["archive_serial_number"] = archive_serial_number
    if archive_serial_number_from is not None:
        kwargs["archive_serial_number_from"] = archive_serial_number_from
    if archive_serial_number_till is not None:
        kwargs["archive_serial_number_till"] = archive_serial_number_till
    if checksum is not None:
        kwargs["checksum"] = checksum
    if ordering is not None:
        kwargs["ordering"] = ordering
    if page is not None:
        kwargs["page"] = page
    docs = client.documents.list(**kwargs)
    return [_filter_fields(doc, return_fields) for doc in docs]


@documents.tool
def get_document(
    id: int,
    include_metadata: bool = False,
    return_fields: list[str] | None = None,
) -> Document:
    """Retrieve a single document by its ID with configurable field selection.

    Args:
        id: Numeric paperless-ngx document ID.
        include_metadata: When True, fetches extended file-level metadata
            concurrently and attaches it to the document. Default: False.
        return_fields: Document fields to include in the response. All others
            are set to None. Defaults to a rich detail set.

    Returns:
        The Document with only return_fields populated.
    """
    if return_fields is None:
        return_fields = _GET_RETURN_FIELDS
    client = get_client()
    doc = client.documents.get(id=id, include_metadata=include_metadata)
    return _filter_fields(doc, return_fields)


@documents.tool
def get_document_metadata(id: int) -> DocumentMetadata:
    """Retrieve file-level technical metadata for a document.

    Returns checksums, file sizes, MIME type, and embedded file metadata
    (e.g. PDF XMP/info tags). This data is not included in list or get
    responses unless explicitly requested.

    Args:
        id: Numeric paperless-ngx document ID.

    Returns:
        DocumentMetadata with checksums, sizes, MIME types, and file metadata.
    """
    client = get_client()
    return client.documents.get_metadata(id=id)


@documents.tool
def update_document(
    id: int,
    title: str | None = None,
    content: str | None = None,
    created: str | None = None,
    correspondent: int | str | None = _UNSET,
    document_type: int | str | None = _UNSET,
    storage_path: int | str | None = _UNSET,
    tags: list[int | str] | None = None,
    archive_serial_number: int | None = _UNSET,
    custom_fields: list[dict[str, Any]] | None = None,
    owner: int | None = _UNSET,
    set_permissions: SetPermissions | None = None,
    remove_inbox_tags: bool | None = None,
) -> Document:
    """Partially update a document (PATCH semantics).

    Only fields that are explicitly provided are sent to the API. Omitting a
    field leaves it unchanged on the server. Passing None for a nullable field
    clears it (removes the assigned value).

    Args:
        id: Numeric ID of the document to update.
        title: New document title.
        content: OCR text content.
        created: Creation date as ISO-8601 string ("YYYY-MM-DD").
        correspondent: Correspondent to assign (ID or name). Omit to leave
            unchanged, or pass None to clear.
        document_type: Document type to assign (ID or name). Omit to leave
            unchanged, or pass None to clear.
        storage_path: Storage path to assign (ID or name). Omit to leave
            unchanged, or pass None to clear.
        tags: Full replacement list of tags (IDs or names).
        archive_serial_number: Archive serial number to assign. Omit to leave
            unchanged, or pass None to clear.
        custom_fields: List of custom field value dicts, each in the form
            {"field": <field_id>, "value": <value>}.
        owner: Numeric user ID to assign as document owner. Omit to leave
            unchanged, or pass None to clear.
        set_permissions: Explicit view/change permission sets.
        remove_inbox_tags: When True, removes all inbox tags from the document.

    Returns:
        The updated Document.
    """
    client = get_client()
    kwargs: dict[str, Any] = {}

    if title is not None:
        kwargs["title"] = title
    if content is not None:
        kwargs["content"] = content
    if created is not None:
        kwargs["created"] = created

    if correspondent is not UNSET:
        kwargs["correspondent"] = correspondent

    if document_type is not UNSET:
        kwargs["document_type"] = document_type

    if storage_path is not UNSET:
        kwargs["storage_path"] = storage_path

    if tags is not None:
        kwargs["tags"] = tags

    if archive_serial_number is not UNSET:
        kwargs["archive_serial_number"] = archive_serial_number

    if custom_fields is not None:
        kwargs["custom_fields"] = custom_fields

    if owner is not UNSET:
        kwargs["owner"] = owner

    if set_permissions is not None:
        kwargs["set_permissions"] = set_permissions

    if remove_inbox_tags is not None:
        kwargs["remove_inbox_tags"] = remove_inbox_tags

    return client.documents.update(id, **kwargs)


@documents.tool
def delete_document(id: int) -> None:
    """Permanently delete a document by its ID.

    This action is irreversible.

    Args:
        id: Numeric ID of the document to delete.
    """
    client = get_client()
    client.documents.delete(id=id)


@documents.tool
def upload_document(
    file_path: str,
    title: str | None = None,
    created: str | None = None,
    correspondent: int | str | None = None,
    document_type: int | str | None = None,
    storage_path: int | str | None = None,
    tags: list[int | str] | None = None,
    archive_serial_number: int | None = None,
    custom_fields: list[dict[str, Any]] | None = None,
    wait: bool = False,
) -> str | Document:
    """Upload a document file to paperless-ngx.

    Args:
        file_path: Absolute path to the file to upload.
        title: Title to assign to the document.
        created: Creation date as ISO-8601 string ("YYYY-MM-DD").
        correspondent: Correspondent to assign (ID or name).
        document_type: Document type to assign (ID or name).
        storage_path: Storage path to assign (ID or name).
        tags: Tags to assign (IDs or names).
        archive_serial_number: Archive serial number to assign.
        custom_fields: List of custom field value dicts, each in the form
            {"field": <field_id>, "value": <value>}.
        wait: If False (default), returns the Celery task ID immediately.
            If True, polls until processing completes and returns the Document.

    Returns:
        The Celery task ID string when wait=False, or the processed Document
        when wait=True.
    """
    client = get_client()
    kwargs: dict[str, Any] = {"wait": wait}
    if title is not None:
        kwargs["title"] = title
    if created is not None:
        kwargs["created"] = created
    if correspondent is not None:
        kwargs["correspondent"] = correspondent
    if document_type is not None:
        kwargs["document_type"] = document_type
    if storage_path is not None:
        kwargs["storage_path"] = storage_path
    if tags is not None:
        kwargs["tags"] = tags
    if archive_serial_number is not None:
        kwargs["archive_serial_number"] = archive_serial_number
    if custom_fields is not None:
        kwargs["custom_fields"] = custom_fields
    return client.documents.upload(file_path, **kwargs)


# ---------------------------------------------------------------------------
# Bulk document tools
# ---------------------------------------------------------------------------


@documents.tool
def bulk_add_tag(ids: list[int], tag: int | str) -> None:
    """Add a tag to multiple documents in a single request.

    Args:
        ids: List of document IDs to tag.
        tag: Tag to add (ID or name).
    """
    client = get_client()
    client.documents.bulk_add_tag(ids, tag)


@documents.tool
def bulk_remove_tag(ids: list[int], tag: int | str) -> None:
    """Remove a tag from multiple documents in a single request.

    Args:
        ids: List of document IDs to un-tag.
        tag: Tag to remove (ID or name).
    """
    client = get_client()
    client.documents.bulk_remove_tag(ids, tag)


@documents.tool
def bulk_modify_tags(
    ids: list[int],
    add_tags: list[int | str] | None = None,
    remove_tags: list[int | str] | None = None,
) -> None:
    """Add and/or remove tags on multiple documents atomically.

    Args:
        ids: List of document IDs to modify.
        add_tags: Tags to add (IDs or names).
        remove_tags: Tags to remove (IDs or names).
    """
    client = get_client()
    client.documents.bulk_modify_tags(ids, add_tags=add_tags, remove_tags=remove_tags)


@documents.tool
def bulk_delete_documents(ids: list[int]) -> None:
    """Permanently delete multiple documents in a single request.

    This action is irreversible.

    Args:
        ids: List of document IDs to delete.
    """
    client = get_client()
    client.documents.bulk_delete(ids)


@documents.tool
def bulk_set_correspondent(
    ids: list[int],
    correspondent: int | str | None,
) -> None:
    """Assign or clear a correspondent on multiple documents.

    Args:
        ids: List of document IDs to modify.
        correspondent: Correspondent to assign (ID or name), or None to clear.
    """
    client = get_client()
    client.documents.bulk_set_correspondent(ids, correspondent)


@documents.tool
def bulk_set_document_type(
    ids: list[int],
    document_type: int | str | None,
) -> None:
    """Assign or clear a document type on multiple documents.

    Args:
        ids: List of document IDs to modify.
        document_type: Document type to assign (ID or name), or None to clear.
    """
    client = get_client()
    client.documents.bulk_set_document_type(ids, document_type)


@documents.tool
def bulk_set_storage_path(
    ids: list[int],
    storage_path: int | str | None,
) -> None:
    """Assign or clear a storage path on multiple documents.

    Args:
        ids: List of document IDs to modify.
        storage_path: Storage path to assign (ID or name), or None to clear.
    """
    client = get_client()
    client.documents.bulk_set_storage_path(ids, storage_path)


@documents.tool
def bulk_modify_custom_fields(
    ids: list[int],
    add_fields: list[dict[str, Any]] | None = None,
    remove_fields: list[int] | None = None,
) -> None:
    """Add and/or remove custom field values on multiple documents.

    Args:
        ids: List of document IDs to modify.
        add_fields: Custom field value dicts to add, each in the form
            {"field": <field_id>, "value": <value>}.
        remove_fields: Custom field IDs whose values should be removed.
    """
    client = get_client()
    client.documents.bulk_modify_custom_fields(
        ids, add_fields=add_fields, remove_fields=remove_fields
    )


@documents.tool
def bulk_set_permissions(
    ids: list[int],
    set_permissions: SetPermissions | None = None,
    owner: int | None = None,
    merge: bool = False,
) -> None:
    """Set permissions and/or owner on multiple documents.

    Args:
        ids: List of document IDs to modify.
        set_permissions: Explicit view/change permission sets. Contains
            view.users, view.groups, change.users, change.groups lists.
        owner: Numeric user ID to assign as document owner.
        merge: When True, new permissions are merged with existing ones.
            Default: False (replace).
    """
    client = get_client()
    client.documents.bulk_set_permissions(
        ids, set_permissions=set_permissions, owner=owner, merge=merge
    )


# ---------------------------------------------------------------------------
# Document notes tools
# ---------------------------------------------------------------------------


@documents.tool
def list_document_notes(id: int) -> list[DocumentNote]:
    """List all notes attached to a document.

    Args:
        id: Numeric ID of the document whose notes to retrieve.

    Returns:
        List of DocumentNote objects ordered by creation time.
    """
    client = get_client()
    return client.documents.notes.list(id)


@documents.tool
def create_document_note(id: int, note: str) -> DocumentNote:
    """Add a note to a document.

    Args:
        id: Numeric ID of the document to annotate.
        note: Text content of the note.

    Returns:
        The created DocumentNote.
    """
    client = get_client()
    return client.documents.notes.create(id, note=note)


@documents.tool
def delete_document_note(id: int, note_id: int) -> None:
    """Delete a note from a document.

    Args:
        id: Numeric ID of the document that owns the note.
        note_id: Numeric ID of the note to delete.
    """
    client = get_client()
    client.documents.notes.delete(id, note_id)
