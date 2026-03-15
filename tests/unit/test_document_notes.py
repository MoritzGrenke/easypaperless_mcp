"""Unit tests for document notes sub-server tools."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from easypaperless import DocumentNote

from easypaperless_mcp.tools.document_notes import (
    create_document_note,
    delete_document_note,
    list_document_notes,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def patch_document_notes_get_client(patch_get_client: MagicMock):
    """Also patch get_client inside the document_notes module."""
    with patch("easypaperless_mcp.tools.document_notes.get_client", return_value=patch_get_client):
        yield patch_get_client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_document_note(**kwargs: Any) -> DocumentNote:
    """Build a minimal DocumentNote with sensible defaults."""
    defaults: dict[str, Any] = {
        "id": 1,
        "note": "Test note",
        "document": 42,
    }
    defaults.update(kwargs)
    return DocumentNote.model_validate(defaults)


# ---------------------------------------------------------------------------
# list_document_notes
# ---------------------------------------------------------------------------


def test_list_document_notes_calls_client(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.notes.list.return_value = [make_document_note(id=1), make_document_note(id=2)]
    result = list_document_notes(document_id=42)
    patch_get_client.documents.notes.list.assert_called_once_with(42)
    assert len(result) == 2


def test_list_document_notes_passes_document_id(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.notes.list.return_value = []
    list_document_notes(document_id=99)
    patch_get_client.documents.notes.list.assert_called_once_with(99)


def test_list_document_notes_returns_empty_list(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.notes.list.return_value = []
    assert list_document_notes(document_id=1) == []


def test_list_document_notes_returns_document_note_objects(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.notes.list.return_value = [make_document_note(id=7, note="Hello")]
    result = list_document_notes(document_id=42)
    assert isinstance(result[0], DocumentNote)
    assert result[0].id == 7
    assert result[0].note == "Hello"


# ---------------------------------------------------------------------------
# create_document_note
# ---------------------------------------------------------------------------


def test_create_document_note_calls_client(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.notes.create.return_value = make_document_note(id=5, note="New note")
    create_document_note(document_id=42, note="New note")
    patch_get_client.documents.notes.create.assert_called_once_with(42, note="New note")


def test_create_document_note_passes_note_as_kwarg(patch_get_client: MagicMock) -> None:
    """note must be passed as a keyword argument to the easypaperless API."""
    patch_get_client.documents.notes.create.return_value = make_document_note(id=1)
    create_document_note(document_id=10, note="kwarg check")
    call_args = patch_get_client.documents.notes.create.call_args
    assert call_args.kwargs.get("note") == "kwarg check"


def test_create_document_note_returns_document_note(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.notes.create.return_value = make_document_note(id=5, note="Created")
    result = create_document_note(document_id=42, note="Created")
    assert isinstance(result, DocumentNote)
    assert result.note == "Created"


def test_create_document_note_passes_correct_document_id(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.notes.create.return_value = make_document_note(id=1)
    create_document_note(document_id=77, note="Note text")
    call_args = patch_get_client.documents.notes.create.call_args
    assert call_args.args[0] == 77


# ---------------------------------------------------------------------------
# delete_document_note
# ---------------------------------------------------------------------------


def test_delete_document_note_calls_client(patch_get_client: MagicMock) -> None:
    delete_document_note(document_id=42, note_id=7)
    patch_get_client.documents.notes.delete.assert_called_once_with(42, 7)


def test_delete_document_note_passes_correct_ids(patch_get_client: MagicMock) -> None:
    delete_document_note(document_id=10, note_id=99)
    call_args = patch_get_client.documents.notes.delete.call_args
    assert call_args.args == (10, 99)


def test_delete_document_note_returns_none(patch_get_client: MagicMock) -> None:
    patch_get_client.documents.notes.delete.return_value = None
    result = delete_document_note(document_id=1, note_id=1)
    assert result is None
