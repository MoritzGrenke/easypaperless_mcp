"""Integration tests for document notes tools against a live paperless-ngx instance."""

import pytest
from easypaperless import DocumentNote, SyncPaperlessClient

from easypaperless_mcp.tools.document_notes import (
    create_document_note,
    delete_document_note,
    list_document_notes,
)
from easypaperless_mcp.tools.documents import list_documents
from easypaperless_mcp.tools.models import ListResult


pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def document_id(paperless_client: SyncPaperlessClient) -> int:
    """Return the ID of the first available document, skipping if none exist."""
    result = list_documents()
    if not result.items:
        pytest.skip("No documents in test instance")
    assert result.items[0].id is not None
    return result.items[0].id


def test_list_document_notes_returns_list_result(
    paperless_client: SyncPaperlessClient, document_id: int
) -> None:
    result = list_document_notes(document_id=document_id)
    assert isinstance(result, ListResult)


def test_list_document_notes_returns_count(
    paperless_client: SyncPaperlessClient, document_id: int
) -> None:
    result = list_document_notes(document_id=document_id)
    assert isinstance(result.count, int)
    assert result.count >= 0


def test_list_document_notes_returns_document_note_objects(
    paperless_client: SyncPaperlessClient, document_id: int
) -> None:
    result = list_document_notes(document_id=document_id)
    for note in result.items:
        assert isinstance(note, DocumentNote)


def test_list_document_notes_pagination_params_accepted(
    paperless_client: SyncPaperlessClient, document_id: int
) -> None:
    """page and page_size parameters should be accepted without error."""
    result = list_document_notes(document_id=document_id, page=1, page_size=10)
    assert isinstance(result, ListResult)


def test_create_and_delete_note_round_trip(
    paperless_client: SyncPaperlessClient, document_id: int
) -> None:
    """Create a note, verify it appears in list, then delete it."""
    note_text = "easypaperless-mcp integration test note"

    created = create_document_note(document_id=document_id, note=note_text)
    assert isinstance(created, DocumentNote)
    assert created.note == note_text
    assert created.id is not None

    notes_after_create = list_document_notes(document_id=document_id)
    note_ids = [n.id for n in notes_after_create.items]
    assert created.id in note_ids

    delete_document_note(document_id=document_id, note_id=created.id)

    notes_after_delete = list_document_notes(document_id=document_id)
    remaining_ids = [n.id for n in notes_after_delete.items]
    assert created.id not in remaining_ids
