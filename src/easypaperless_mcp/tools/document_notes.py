"""Document notes sub-server: MCP tools for the paperless-ngx document notes sub-resource."""

from easypaperless import DocumentNote
from fastmcp import FastMCP

from ..client import get_client
from .models import ListResult

document_notes = FastMCP("document_notes")


@document_notes.tool
def list_document_notes(
    document_id: int,
    page: int | None = None,
    page_size: int | None = None,
) -> ListResult[DocumentNote]:
    """List all notes attached to a document.

    Args:
        document_id: Numeric paperless-ngx document ID.
        page: Page number to retrieve (1-based). Omit to retrieve the first page.
        page_size: Number of notes per page. Omit to use the server default.

    Returns:
        ListResult with count (total notes for this document in paperless-ngx)
        and items (notes on the requested page).
    """
    client = get_client()
    paged = client.documents.notes.list(document_id, page=page, page_size=page_size)
    return ListResult(count=paged.count, items=paged.results)


@document_notes.tool
def create_document_note(document_id: int, note: str) -> DocumentNote:
    """Add a new note to a document.

    Args:
        document_id: Numeric paperless-ngx document ID.
        note: Text content of the note to create.

    Returns:
        The created DocumentNote.
    """
    client = get_client()
    return client.documents.notes.create(document_id, note=note)


@document_notes.tool
def delete_document_note(document_id: int, note_id: int) -> None:
    """Permanently delete a note from a document.

    This action is irreversible.

    Args:
        document_id: Numeric paperless-ngx document ID.
        note_id: Numeric ID of the note to delete.
    """
    client = get_client()
    client.documents.notes.delete(document_id, note_id)
