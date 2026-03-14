"""Unit tests for documents sub-server tools."""

from unittest.mock import MagicMock

from easypaperless_mcp.tools.documents import (
    _filter_fields,
    delete_document,
    get_document,
    list_documents,
    update_document,
)

from .conftest import make_document


# ---------------------------------------------------------------------------
# _filter_fields
# ---------------------------------------------------------------------------


def test_filter_fields_keeps_listed_fields() -> None:
    doc = make_document(id=42, title="Keep Me")
    result = _filter_fields(doc, ["id", "title"])
    assert result.id == 42
    assert result.title == "Keep Me"


def test_filter_fields_nulls_unlisted_fields() -> None:
    doc = make_document(correspondent=5)
    result = _filter_fields(doc, ["id", "title"])
    assert result.correspondent is None


def test_filter_fields_noop_when_all_listed() -> None:
    doc = make_document()
    all_fields = list(doc.__class__.model_fields.keys())
    result = _filter_fields(doc, all_fields)
    assert result is doc


# ---------------------------------------------------------------------------
# list_documents
# ---------------------------------------------------------------------------


def test_list_documents_calls_client(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = [make_document(id=1), make_document(id=2)]
    result = list_documents()
    patch_get_client.documents.list.assert_called_once()
    assert len(result) == 2


def test_list_documents_applies_field_filter(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = [make_document(correspondent=99)]
    result = list_documents(return_fields=["id", "title"])
    assert result[0].correspondent is None


def test_list_documents_passes_search(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = []
    list_documents(search="invoice", search_mode="title")
    call_kwargs = patch_get_client.documents.list.call_args.kwargs
    assert call_kwargs["search"] == "invoice"
    assert call_kwargs["search_mode"] == "title"


def test_list_documents_omits_none_filters(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = []
    list_documents()
    call_kwargs = patch_get_client.documents.list.call_args.kwargs
    assert "search" not in call_kwargs
    assert "tags" not in call_kwargs


def test_list_documents_passes_ids(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = []
    list_documents(ids=[1, 2, 3])
    assert patch_get_client.documents.list.call_args.kwargs["ids"] == [1, 2, 3]


def test_list_documents_passes_any_and_exclude_tags(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = []
    list_documents(any_tags=[1, "urgent"], exclude_tags=[5])
    call_kwargs = patch_get_client.documents.list.call_args.kwargs
    assert call_kwargs["any_tags"] == [1, "urgent"]
    assert call_kwargs["exclude_tags"] == [5]


def test_list_documents_passes_correspondent_filters(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = []
    list_documents(any_correspondent=[1, 2], exclude_correspondents=[3])
    call_kwargs = patch_get_client.documents.list.call_args.kwargs
    assert call_kwargs["any_correspondent"] == [1, 2]
    assert call_kwargs["exclude_correspondents"] == [3]


def test_list_documents_passes_document_type_filters(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = []
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
    patch_get_client.documents.list.return_value = []
    list_documents(any_storage_paths=[1], exclude_storage_paths=[2])
    call_kwargs = patch_get_client.documents.list.call_args.kwargs
    assert call_kwargs["any_storage_paths"] == [1]
    assert call_kwargs["exclude_storage_paths"] == [2]


def test_list_documents_passes_owner_filters(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = []
    list_documents(owner=7, exclude_owners=[8, 9])
    call_kwargs = patch_get_client.documents.list.call_args.kwargs
    assert call_kwargs["owner"] == 7
    assert call_kwargs["exclude_owners"] == [8, 9]


def test_list_documents_passes_custom_field_filters(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = []
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
    patch_get_client.documents.list.return_value = []
    list_documents(archive_serial_number=42, archive_serial_number_from=10, archive_serial_number_till=50)
    call_kwargs = patch_get_client.documents.list.call_args.kwargs
    assert call_kwargs["archive_serial_number"] == 42
    assert call_kwargs["archive_serial_number_from"] == 10
    assert call_kwargs["archive_serial_number_till"] == 50


def test_list_documents_passes_date_filters(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = []
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
    patch_get_client.documents.list.return_value = []
    list_documents(checksum="abc123def456")
    assert patch_get_client.documents.list.call_args.kwargs["checksum"] == "abc123def456"


def test_list_documents_passes_pagination_params(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = []
    list_documents(page=2, page_size=50, descending=True)
    call_kwargs = patch_get_client.documents.list.call_args.kwargs
    assert call_kwargs["page"] == 2
    assert call_kwargs["page_size"] == 50
    assert call_kwargs["descending"] is True


def test_list_documents_page_omitted_when_none(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.list.return_value = []
    list_documents()
    assert "page" not in patch_get_client.documents.list.call_args.kwargs


# ---------------------------------------------------------------------------
# get_document
# ---------------------------------------------------------------------------


def test_get_document_returns_filtered(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.get.return_value = make_document(id=7, content="secret")
    result = get_document(7, return_fields=["id"])
    patch_get_client.documents.get.assert_called_once_with(id=7)
    assert result.id == 7
    assert result.content is None


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


def test_update_document_clear_correspondent(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.update.return_value = make_document(id=1)
    update_document(1, clear_correspondent=True)
    call_kwargs = patch_get_client.documents.update.call_args.kwargs
    assert call_kwargs["correspondent"] is None


# ---------------------------------------------------------------------------
# delete_document
# ---------------------------------------------------------------------------


def test_delete_document_calls_client(patch_get_client: MagicMock) -> None:
    delete_document(99)
    patch_get_client.documents.delete.assert_called_once_with(id=99)
