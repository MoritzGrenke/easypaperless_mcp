"""Unit tests for documents sub-server tools."""

from unittest.mock import MagicMock

from easypaperless import DocumentMetadata, SetPermissions

from easypaperless_mcp.tools.documents import (
    _OMITTED_FIELDS_HINT,
    _compute_omitted_fields,
    _filter_fields,
    bulk_add_tag,
    bulk_delete_documents,
    bulk_modify_custom_fields,
    bulk_modify_tags,
    bulk_remove_tag,
    bulk_set_correspondent,
    bulk_set_document_type,
    bulk_set_permissions,
    bulk_set_storage_path,
    delete_document,
    get_document,
    get_document_metadata,
    list_documents,
    update_document,
    upload_document,
)

from .conftest import make_document


# ---------------------------------------------------------------------------
# _filter_fields
# ---------------------------------------------------------------------------


def test_filter_fields_keeps_listed_fields() -> None:
    doc = make_document(id=42, title="Keep Me")
    result = _filter_fields(doc, ["id", "title"])
    assert result["id"] == 42
    assert result["title"] == "Keep Me"


def test_filter_fields_excludes_unlisted_fields() -> None:
    doc = make_document(correspondent=5)
    result = _filter_fields(doc, ["id", "title"])
    assert "correspondent" not in result


def test_filter_fields_all_listed_returns_full_dict() -> None:
    doc = make_document()
    all_fields = list(doc.__class__.model_fields.keys())
    result = _filter_fields(doc, all_fields)
    assert set(result.keys()) == set(all_fields)


def test_filter_fields_returns_only_requested_keys() -> None:
    doc = make_document(tags=[1, 2], notes=[], custom_fields=[])
    result = _filter_fields(doc, ["id", "title"])
    assert "tags" not in result
    assert "notes" not in result
    assert "custom_fields" not in result
    assert set(result.keys()) == {"id", "title"}


def test_filter_fields_unknown_field_silently_skipped() -> None:
    doc = make_document(id=1)
    result = _filter_fields(doc, ["id", "nonexistent_field"])
    assert set(result.keys()) == {"id"}


# ---------------------------------------------------------------------------
# _compute_omitted_fields
# ---------------------------------------------------------------------------


def test_compute_omitted_fields_returns_omitted_names_and_hint() -> None:
    doc = make_document(id=1, correspondent=5)
    omitted = _compute_omitted_fields(doc, ["id", "title"])
    all_fields = set(doc.__class__.model_fields)
    expected_names = sorted(f for f in all_fields if f not in {"id", "title"})
    assert omitted[:-1] == expected_names
    assert omitted[-1] == _OMITTED_FIELDS_HINT


def test_compute_omitted_fields_empty_when_all_included() -> None:
    doc = make_document()
    all_fields = list(doc.__class__.model_fields.keys())
    omitted = _compute_omitted_fields(doc, all_fields)
    assert omitted == []


def test_compute_omitted_fields_hint_is_last_element() -> None:
    doc = make_document()
    omitted = _compute_omitted_fields(doc, ["id"])
    assert omitted[-1] == _OMITTED_FIELDS_HINT


# ---------------------------------------------------------------------------
# list_documents
# ---------------------------------------------------------------------------


def test_list_documents_calls_client(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = MagicMock(count=2, results=[make_document(id=1), make_document(id=2)])
    result = list_documents()
    patch_get_client.documents.list.assert_called_once()
    assert result.count == 2
    assert len(result.items) == 2


def test_list_documents_applies_field_filter(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = MagicMock(count=1, results=[make_document(correspondent=99)])
    result = list_documents(return_fields=["id", "title"])
    assert "correspondent" not in result.items[0]


def test_list_documents_return_fields_id_title_only(patch_get_client: MagicMock) -> None:
    """Only id and title appear in items; all other fields are absent."""
    patch_get_client.documents.list.return_value = MagicMock(count=1, results=[
        make_document(id=5, title="Hello", correspondent=3, document_type=2, tags=[1], archive_serial_number=99)
    ])
    result = list_documents(return_fields=["id", "title"])
    item = result.items[0]
    assert item["id"] == 5
    assert item["title"] == "Hello"
    assert "correspondent" not in item
    assert "document_type" not in item
    assert "tags" not in item
    assert "archive_serial_number" not in item
    assert "created" not in item
    assert "content" not in item


def test_list_documents_default_return_fields_preserves_list_fields(patch_get_client: MagicMock) -> None:
    """Default return_fields keeps exactly _LIST_RETURN_FIELDS; content is absent."""
    patch_get_client.documents.list.return_value = MagicMock(count=1, results=[
        make_document(id=1, title="T", correspondent=7, tags=[2], archive_serial_number=10, content="secret")
    ])
    result = list_documents(return_fields=None)
    item = result.items[0]
    assert item["id"] == 1
    assert item["title"] == "T"
    assert item["correspondent"] == 7
    assert item["tags"] == [2]
    assert item["archive_serial_number"] == 10
    assert "content" not in item


def test_list_documents_field_filter_applied_to_all_results(patch_get_client: MagicMock) -> None:
    """return_fields filter is applied to every document in the result list."""
    patch_get_client.documents.list.return_value = MagicMock(count=3, results=[
        make_document(id=1, correspondent=10),
        make_document(id=2, correspondent=20),
        make_document(id=3, correspondent=30),
    ])
    result = list_documents(return_fields=["id"])
    assert all("correspondent" not in item for item in result.items)
    assert [item["id"] for item in result.items] == [1, 2, 3]


def test_list_documents_empty_result(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = MagicMock(count=0, results=[])
    result = list_documents()
    assert result.count == 0
    assert result.items == []


def test_list_documents_count_reflects_total_not_page(patch_get_client: MagicMock) -> None:
    """count is the total from the server, not just len(items)."""
    patch_get_client.documents.list.return_value = MagicMock(count=150, results=[make_document(id=1)])
    result = list_documents()
    assert result.count == 150
    assert len(result.items) == 1


def test_list_documents_passes_created_date_filters(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = MagicMock(count=0, results=[])
    list_documents(created_after="2023-01-01", created_before="2023-12-31")
    call_kwargs = patch_get_client.documents.list.call_args.kwargs
    assert call_kwargs["created_after"] == "2023-01-01"
    assert call_kwargs["created_before"] == "2023-12-31"


def test_list_documents_default_pagination_always_passed(patch_get_client: MagicMock) -> None:
    """page_size and descending are always forwarded even at their defaults."""
    patch_get_client.documents.list.return_value = MagicMock(count=0, results=[])
    list_documents()
    call_kwargs = patch_get_client.documents.list.call_args.kwargs
    assert call_kwargs["page_size"] == 25
    assert call_kwargs["descending"] is False


def test_list_documents_passes_search(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = MagicMock(count=0, results=[])
    list_documents(search="invoice", search_mode="title")
    call_kwargs = patch_get_client.documents.list.call_args.kwargs
    assert call_kwargs["search"] == "invoice"
    assert call_kwargs["search_mode"] == "title"


def test_list_documents_omits_none_filters(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = MagicMock(count=0, results=[])
    list_documents()
    call_kwargs = patch_get_client.documents.list.call_args.kwargs
    assert "search" not in call_kwargs
    assert "tags" not in call_kwargs


def test_list_documents_always_includes_id_even_when_omitted(patch_get_client: MagicMock) -> None:
    """Regression: id must be in the result even when caller omits it from return_fields."""
    patch_get_client.documents.list.return_value = MagicMock(
        count=1, results=[make_document(id=7, title="Doc")]
    )
    result = list_documents(return_fields=["created", "tags"])
    assert result.items[0]["id"] == 7


def test_list_documents_return_fields_omitting_id_and_title(patch_get_client: MagicMock) -> None:
    """Regression: list_documents with return_fields=["created","tags"] succeeds without error."""
    patch_get_client.documents.list.return_value = MagicMock(
        count=1,
        results=[make_document(id=3, title="Hello", correspondent=5)],
    )
    result = list_documents(return_fields=["created", "tags"])
    item = result.items[0]
    assert item["id"] == 3        # silently added
    assert "title" not in item    # excluded from return_fields
    assert "correspondent" not in item


def test_list_documents_omitted_fields_on_result(patch_get_client: MagicMock) -> None:
    """omitted_fields on ListResult lists excluded field names plus hint."""
    patch_get_client.documents.list.return_value = MagicMock(
        count=1, results=[make_document(id=1, content="text")]
    )
    result = list_documents(return_fields=["id", "title"])
    assert len(result.omitted_fields) > 1
    assert "content" in result.omitted_fields
    assert result.omitted_fields[-1] == _OMITTED_FIELDS_HINT


def test_list_documents_omitted_fields_empty_when_all_fields_included(patch_get_client: MagicMock) -> None:
    """omitted_fields is empty when all model fields are requested."""
    doc = make_document()
    all_fields = list(doc.__class__.model_fields.keys())
    patch_get_client.documents.list.return_value = MagicMock(count=1, results=[doc])
    result = list_documents(return_fields=all_fields)
    assert result.omitted_fields == []


def test_list_documents_omitted_fields_empty_for_empty_results(patch_get_client: MagicMock) -> None:
    """omitted_fields is empty when no results are returned."""
    patch_get_client.documents.list.return_value = MagicMock(count=0, results=[])
    result = list_documents(return_fields=["id"])
    assert result.omitted_fields == []


def test_list_documents_passes_ids(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = MagicMock(count=0, results=[])
    list_documents(ids=[1, 2, 3])
    assert patch_get_client.documents.list.call_args.kwargs["ids"] == [1, 2, 3]


def test_list_documents_passes_any_and_exclude_tags(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = MagicMock(count=0, results=[])
    list_documents(any_tags=[1, "urgent"], exclude_tags=[5])
    call_kwargs = patch_get_client.documents.list.call_args.kwargs
    assert call_kwargs["any_tags"] == [1, "urgent"]
    assert call_kwargs["exclude_tags"] == [5]


def test_list_documents_passes_correspondent_filters(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = MagicMock(count=0, results=[])
    list_documents(any_correspondent=[1, 2], exclude_correspondents=[3])
    call_kwargs = patch_get_client.documents.list.call_args.kwargs
    assert call_kwargs["any_correspondent"] == [1, 2]
    assert call_kwargs["exclude_correspondents"] == [3]


def test_list_documents_passes_document_type_filters(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = MagicMock(count=0, results=[])
    list_documents(
        document_type_name_contains="invoice",
        document_type_name_exact="Invoice",
        any_document_type=[1, 2],
        exclude_document_types=[3],
    )
    call_kwargs = patch_get_client.documents.list.call_args.kwargs
    assert call_kwargs["document_type_name_contains"] == "invoice"
    assert call_kwargs["document_type_name_exact"] == "Invoice"
    assert call_kwargs["any_document_type"] == [1, 2]
    assert call_kwargs["exclude_document_types"] == [3]


def test_list_documents_passes_storage_path_filters(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = MagicMock(count=0, results=[])
    list_documents(any_storage_paths=[1], exclude_storage_paths=[2])
    call_kwargs = patch_get_client.documents.list.call_args.kwargs
    assert call_kwargs["any_storage_paths"] == [1]
    assert call_kwargs["exclude_storage_paths"] == [2]


def test_list_documents_passes_owner_filters(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = MagicMock(count=0, results=[])
    list_documents(owner=7, exclude_owners=[8, 9])
    call_kwargs = patch_get_client.documents.list.call_args.kwargs
    assert call_kwargs["owner"] == 7
    assert call_kwargs["exclude_owners"] == [8, 9]


def test_list_documents_passes_custom_field_filters(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = MagicMock(count=0, results=[])
    query = ["AND", [["1", "exact", "foo"]]]
    list_documents(
        custom_fields=[1],
        any_custom_fields=[2],
        exclude_custom_fields=[3],
        custom_field_query=query,
    )
    call_kwargs = patch_get_client.documents.list.call_args.kwargs
    assert call_kwargs["custom_fields"] == [1]
    assert call_kwargs["any_custom_fields"] == [2]
    assert call_kwargs["exclude_custom_fields"] == [3]
    assert call_kwargs["custom_field_query"] == query


def test_list_documents_passes_asn_filters(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = MagicMock(count=0, results=[])
    list_documents(archive_serial_number=42, archive_serial_number_from=10, archive_serial_number_till=50)
    call_kwargs = patch_get_client.documents.list.call_args.kwargs
    assert call_kwargs["archive_serial_number"] == 42
    assert call_kwargs["archive_serial_number_from"] == 10
    assert call_kwargs["archive_serial_number_till"] == 50


def test_list_documents_passes_date_filters(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = MagicMock(count=0, results=[])
    list_documents(
        added_after="2024-01-01T00:00:00Z",
        added_before="2024-12-31T23:59:59Z",
        modified_after="2024-06-01T00:00:00Z",
        modified_before="2024-06-30T23:59:59Z",
    )
    call_kwargs = patch_get_client.documents.list.call_args.kwargs
    assert call_kwargs["added_after"] == "2024-01-01T00:00:00Z"
    assert call_kwargs["added_before"] == "2024-12-31T23:59:59Z"
    assert call_kwargs["modified_after"] == "2024-06-01T00:00:00Z"
    assert call_kwargs["modified_before"] == "2024-06-30T23:59:59Z"


def test_list_documents_passes_checksum(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = MagicMock(count=0, results=[])
    list_documents(checksum="abc123def456")
    assert patch_get_client.documents.list.call_args.kwargs["checksum"] == "abc123def456"


def test_list_documents_passes_pagination_params(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = MagicMock(count=0, results=[])
    list_documents(page=2, page_size=50, descending=True)
    call_kwargs = patch_get_client.documents.list.call_args.kwargs
    assert call_kwargs["page"] == 2
    assert call_kwargs["page_size"] == 50
    assert call_kwargs["descending"] is True


def test_list_documents_page_omitted_when_none(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = MagicMock(count=0, results=[])
    list_documents()
    assert "page" not in patch_get_client.documents.list.call_args.kwargs


# ---------------------------------------------------------------------------
# get_document
# ---------------------------------------------------------------------------


def test_get_document_returns_filtered(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.get.return_value = make_document(id=7, content="secret")
    result = get_document(7, return_fields=["id"])
    patch_get_client.documents.get.assert_called_once_with(id=7, include_metadata=False)
    assert result["id"] == 7
    assert "content" not in result


def test_get_document_always_includes_id_even_when_omitted(patch_get_client: MagicMock) -> None:
    """Regression: id is silently re-added when caller omits it from return_fields."""
    patch_get_client.documents.get.return_value = make_document(id=55, title="T")
    result = get_document(55, return_fields=["created"])
    assert result["id"] == 55


def test_get_document_return_fields_omitting_title(patch_get_client: MagicMock) -> None:
    """Regression: get_document with return_fields=["created"] excludes title from result."""
    patch_get_client.documents.get.return_value = make_document(id=10, title="Important")
    result = get_document(10, return_fields=["created"])
    assert result["id"] == 10   # silently added
    assert "title" not in result


def test_get_document_default_return_fields_excludes_content(patch_get_client: MagicMock) -> None:
    """content is not in _GET_RETURN_FIELDS so it is absent from the default response."""
    patch_get_client.documents.get.return_value = make_document(id=3, content="full text here")
    result = get_document(3)
    assert "content" not in result


def test_get_document_default_return_fields_preserves_get_fields(patch_get_client: MagicMock) -> None:
    """All fields in _GET_RETURN_FIELDS are present with their values."""
    patch_get_client.documents.get.return_value = make_document(
        id=4, title="My Doc", correspondent=2, document_type=1,
        storage_path=3, tags=[5], archive_serial_number=7, original_file_name="doc.pdf"
    )
    result = get_document(4)
    assert result["id"] == 4
    assert result["title"] == "My Doc"
    assert result["correspondent"] == 2
    assert result["document_type"] == 1
    assert result["storage_path"] == 3
    assert result["tags"] == [5]
    assert result["archive_serial_number"] == 7
    assert result["original_file_name"] == "doc.pdf"


def test_get_document_includes_omitted_fields_metadata(patch_get_client: MagicMock) -> None:
    """omitted_fields key lists excluded fields and the retrieval hint."""
    patch_get_client.documents.get.return_value = make_document(id=1, content="text")
    result = get_document(1, return_fields=["id", "title"])
    assert "omitted_fields" in result
    assert "content" in result["omitted_fields"]
    assert result["omitted_fields"][-1] == _OMITTED_FIELDS_HINT


def test_get_document_no_omitted_fields_when_all_requested(patch_get_client: MagicMock) -> None:
    """omitted_fields is absent when all model fields are requested."""
    doc = make_document(id=1)
    all_fields = list(doc.__class__.model_fields.keys())
    patch_get_client.documents.get.return_value = doc
    result = get_document(1, return_fields=all_fields)
    assert "omitted_fields" not in result


# ---------------------------------------------------------------------------
# get_document_metadata
# ---------------------------------------------------------------------------


def test_get_document_metadata_calls_client(patch_get_client: MagicMock) -> None:
    mock_meta = MagicMock(spec=DocumentMetadata)
    patch_get_client.documents.get_metadata.return_value = mock_meta
    result = get_document_metadata(42)
    patch_get_client.documents.get_metadata.assert_called_once_with(id=42)
    assert result is mock_meta


# ---------------------------------------------------------------------------
# update_document
# ---------------------------------------------------------------------------


def test_update_document_only_sends_provided_fields(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.update.return_value = make_document(id=1, title="New")
    update_document(1, title="New")
    call_args = patch_get_client.documents.update.call_args
    assert call_args.args[0] == 1
    assert call_args.kwargs.get("title") == "New"
    assert "content" not in call_args.kwargs


def test_update_document_none_clears_correspondent(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.update.return_value = make_document(id=1)
    update_document(1, correspondent=None)
    call_kwargs = patch_get_client.documents.update.call_args.kwargs
    assert call_kwargs["correspondent"] is None


def test_update_document_none_clears_document_type(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.update.return_value = make_document(id=1)
    update_document(1, document_type=None)
    assert patch_get_client.documents.update.call_args.kwargs["document_type"] is None


def test_update_document_none_clears_storage_path(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.update.return_value = make_document(id=1)
    update_document(1, storage_path=None)
    assert patch_get_client.documents.update.call_args.kwargs["storage_path"] is None


def test_update_document_none_clears_archive_serial_number(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.update.return_value = make_document(id=1)
    update_document(1, archive_serial_number=None)
    assert patch_get_client.documents.update.call_args.kwargs["archive_serial_number"] is None


def test_update_document_passes_content_and_created(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.update.return_value = make_document(id=1)
    update_document(1, content="new text", created="2024-06-01")
    call_kwargs = patch_get_client.documents.update.call_args.kwargs
    assert call_kwargs["content"] == "new text"
    assert call_kwargs["created"] == "2024-06-01"


def test_update_document_passes_tags(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.update.return_value = make_document(id=1)
    update_document(1, tags=[3, "inbox"])
    assert patch_get_client.documents.update.call_args.kwargs["tags"] == [3, "inbox"]


def test_update_document_passes_remove_inbox_tags(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.update.return_value = make_document(id=1)
    update_document(1, remove_inbox_tags=True)
    assert patch_get_client.documents.update.call_args.kwargs["remove_inbox_tags"] is True


def test_update_document_omits_correspondent_when_not_provided(patch_get_client: MagicMock) -> None:
    """Omitting correspondent sends nothing to the API (UNSET behavior)."""
    patch_get_client.documents.update.return_value = make_document(id=1)
    update_document(1, title="X")
    assert "correspondent" not in patch_get_client.documents.update.call_args.kwargs


def test_update_document_no_kwargs_sent_for_none_fields(patch_get_client: MagicMock) -> None:
    """Calling with only id sends no extra kwargs."""
    patch_get_client.documents.update.return_value = make_document(id=1)
    update_document(1)
    assert patch_get_client.documents.update.call_args.kwargs == {}


# ---------------------------------------------------------------------------
# delete_document
# ---------------------------------------------------------------------------


def test_delete_document_calls_client(patch_get_client: MagicMock) -> None:
    delete_document(99)
    patch_get_client.documents.delete.assert_called_once_with(id=99)


# ---------------------------------------------------------------------------
# upload_document
# ---------------------------------------------------------------------------


def test_upload_document_minimal_call(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.upload.return_value = "task-id-abc"
    result = upload_document("/tmp/file.pdf")
    patch_get_client.documents.upload.assert_called_once_with("/tmp/file.pdf", wait=False)
    assert result == "task-id-abc"


def test_upload_document_passes_optional_fields(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.upload.return_value = "task-id-xyz"
    upload_document(
        "/tmp/invoice.pdf",
        title="Invoice",
        created="2024-03-01",
        correspondent=2,
        document_type=1,
        storage_path=3,
        tags=[4, "finance"],
        archive_serial_number=99,
    )
    call_kwargs = patch_get_client.documents.upload.call_args.kwargs
    assert call_kwargs["title"] == "Invoice"
    assert call_kwargs["created"] == "2024-03-01"
    assert call_kwargs["correspondent"] == 2
    assert call_kwargs["document_type"] == 1
    assert call_kwargs["storage_path"] == 3
    assert call_kwargs["tags"] == [4, "finance"]
    assert call_kwargs["archive_serial_number"] == 99


def test_upload_document_omits_none_optional_fields(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.upload.return_value = "task-id"
    upload_document("/tmp/file.pdf")
    call_kwargs = patch_get_client.documents.upload.call_args.kwargs
    assert "title" not in call_kwargs
    assert "correspondent" not in call_kwargs
    assert "tags" not in call_kwargs


def test_upload_document_wait_true(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.upload.return_value = make_document(id=10)
    result = upload_document("/tmp/file.pdf", wait=True)
    assert patch_get_client.documents.upload.call_args.kwargs["wait"] is True
    assert result.id == 10  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# bulk tools
# ---------------------------------------------------------------------------


def test_bulk_add_tag_calls_client(patch_get_client: MagicMock) -> None:
    bulk_add_tag([1, 2, 3], "urgent")
    patch_get_client.documents.bulk_add_tag.assert_called_once_with([1, 2, 3], "urgent")


def test_bulk_remove_tag_calls_client(patch_get_client: MagicMock) -> None:
    bulk_remove_tag([4, 5], 7)
    patch_get_client.documents.bulk_remove_tag.assert_called_once_with([4, 5], 7)


def test_bulk_modify_tags_passes_add_and_remove(patch_get_client: MagicMock) -> None:
    bulk_modify_tags([1, 2], add_tags=[3], remove_tags=[4])
    patch_get_client.documents.bulk_modify_tags.assert_called_once_with(
        [1, 2], add_tags=[3], remove_tags=[4]
    )


def test_bulk_modify_tags_none_values_passed_through(patch_get_client: MagicMock) -> None:
    bulk_modify_tags([1])
    patch_get_client.documents.bulk_modify_tags.assert_called_once_with(
        [1], add_tags=None, remove_tags=None
    )


def test_bulk_delete_documents_calls_client(patch_get_client: MagicMock) -> None:
    bulk_delete_documents([10, 11, 12])
    patch_get_client.documents.bulk_delete.assert_called_once_with([10, 11, 12])


def test_bulk_set_correspondent_assigns_value(patch_get_client: MagicMock) -> None:
    bulk_set_correspondent([1, 2], "ACME")
    patch_get_client.documents.bulk_set_correspondent.assert_called_once_with([1, 2], "ACME")


def test_bulk_set_correspondent_clears_with_none(patch_get_client: MagicMock) -> None:
    bulk_set_correspondent([1, 2], None)
    patch_get_client.documents.bulk_set_correspondent.assert_called_once_with([1, 2], None)


def test_bulk_set_document_type_calls_client(patch_get_client: MagicMock) -> None:
    bulk_set_document_type([3], 5)
    patch_get_client.documents.bulk_set_document_type.assert_called_once_with([3], 5)


def test_bulk_set_storage_path_calls_client(patch_get_client: MagicMock) -> None:
    bulk_set_storage_path([7, 8], 2)
    patch_get_client.documents.bulk_set_storage_path.assert_called_once_with([7, 8], 2)


def test_bulk_modify_custom_fields_passes_add_and_remove(patch_get_client: MagicMock) -> None:
    add = [{"field": 1, "value": "foo"}]
    bulk_modify_custom_fields([1, 2], add_fields=add, remove_fields=[3])
    patch_get_client.documents.bulk_modify_custom_fields.assert_called_once_with(
        [1, 2], add_fields=add, remove_fields=[3]
    )


def test_bulk_modify_custom_fields_none_values_passed_through(patch_get_client: MagicMock) -> None:
    bulk_modify_custom_fields([1])
    patch_get_client.documents.bulk_modify_custom_fields.assert_called_once_with(
        [1], add_fields=None, remove_fields=None
    )


def test_bulk_set_permissions_with_owner_and_merge(patch_get_client: MagicMock) -> None:
    bulk_set_permissions([1, 2], owner=5, merge=True)
    patch_get_client.documents.bulk_set_permissions.assert_called_once_with(
        [1, 2], set_permissions=None, owner=5, merge=True
    )


def test_bulk_set_permissions_with_set_permissions(patch_get_client: MagicMock) -> None:
    perms = MagicMock(spec=SetPermissions)
    bulk_set_permissions([3], set_permissions=perms)
    patch_get_client.documents.bulk_set_permissions.assert_called_once_with(
        [3], set_permissions=perms, owner=None, merge=False
    )


# ---------------------------------------------------------------------------
# get_document — include_metadata
# ---------------------------------------------------------------------------


def test_get_document_passes_include_metadata_false_by_default(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.get.return_value = make_document(id=1)
    get_document(1)
    patch_get_client.documents.get.assert_called_once_with(id=1, include_metadata=False)


def test_get_document_passes_include_metadata_true(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.get.return_value = make_document(id=1)
    get_document(1, include_metadata=True)
    patch_get_client.documents.get.assert_called_once_with(id=1, include_metadata=True)


def test_get_document_returns_dict(patch_get_client: MagicMock) -> None:
    """get_document returns a plain dict, not a Document model."""
    patch_get_client.documents.get.return_value = make_document(id=1)
    result = get_document(1)
    assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# update_document — custom_fields, owner/clear_owner, set_permissions
# ---------------------------------------------------------------------------


def test_update_document_passes_custom_fields(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.update.return_value = make_document(id=1)
    fields = [{"field": 1, "value": "foo"}, {"field": 2, "value": 42}]
    update_document(1, custom_fields=fields)
    assert patch_get_client.documents.update.call_args.kwargs["custom_fields"] == fields


def test_update_document_passes_owner(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.update.return_value = make_document(id=1)
    update_document(1, owner=7)
    assert patch_get_client.documents.update.call_args.kwargs["owner"] == 7


def test_update_document_none_clears_owner(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.update.return_value = make_document(id=1)
    update_document(1, owner=None)
    assert patch_get_client.documents.update.call_args.kwargs["owner"] is None


def test_update_document_omits_owner_when_not_provided(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.update.return_value = make_document(id=1)
    update_document(1, title="X")
    assert "owner" not in patch_get_client.documents.update.call_args.kwargs


def test_update_document_passes_set_permissions(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.update.return_value = make_document(id=1)
    perms = MagicMock(spec=SetPermissions)
    update_document(1, set_permissions=perms)
    assert patch_get_client.documents.update.call_args.kwargs["set_permissions"] is perms


def test_update_document_omits_set_permissions_when_not_provided(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.update.return_value = make_document(id=1)
    update_document(1, title="X")
    assert "set_permissions" not in patch_get_client.documents.update.call_args.kwargs


# ---------------------------------------------------------------------------
# upload_document — custom_fields
# ---------------------------------------------------------------------------


def test_upload_document_passes_custom_fields(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.upload.return_value = "task-id"
    fields = [{"field": 3, "value": "bar"}]
    upload_document("/tmp/file.pdf", custom_fields=fields)
    assert patch_get_client.documents.upload.call_args.kwargs["custom_fields"] == fields


def test_upload_document_omits_custom_fields_when_none(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.upload.return_value = "task-id"
    upload_document("/tmp/file.pdf")
    assert "custom_fields" not in patch_get_client.documents.upload.call_args.kwargs


# ---------------------------------------------------------------------------
# list_documents — inclusive date bounds
# ---------------------------------------------------------------------------


def test_list_documents_passes_added_from_and_until(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = MagicMock(count=0, results=[])
    list_documents(added_from="2024-01-01T00:00:00Z", added_until="2024-12-31T23:59:59Z")
    call_kwargs = patch_get_client.documents.list.call_args.kwargs
    assert call_kwargs["added_from"] == "2024-01-01T00:00:00Z"
    assert call_kwargs["added_until"] == "2024-12-31T23:59:59Z"


def test_list_documents_passes_modified_from_and_until(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = MagicMock(count=0, results=[])
    list_documents(modified_from="2024-06-01T00:00:00Z", modified_until="2024-06-30T23:59:59Z")
    call_kwargs = patch_get_client.documents.list.call_args.kwargs
    assert call_kwargs["modified_from"] == "2024-06-01T00:00:00Z"
    assert call_kwargs["modified_until"] == "2024-06-30T23:59:59Z"


def test_list_documents_omits_inclusive_date_bounds_when_none(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = MagicMock(count=0, results=[])
    list_documents()
    call_kwargs = patch_get_client.documents.list.call_args.kwargs
    assert "added_from" not in call_kwargs
    assert "added_until" not in call_kwargs
    assert "modified_from" not in call_kwargs
    assert "modified_until" not in call_kwargs

