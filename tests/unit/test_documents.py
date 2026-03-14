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
