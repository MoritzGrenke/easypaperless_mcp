"""Document history sub-server: MCP tools for the paperless-ngx document history sub-resource."""

from easypaperless import AuditLogActor, AuditLogEntry
from fastmcp import FastMCP

from ..client import get_client
from .models import ListResult

document_history = FastMCP("document_history")


@document_history.tool
def get_document_history(
    id: int,
    page: int | None = None,
    page_size: int | None = None,
) -> ListResult[AuditLogEntry]:
    """Retrieve the full audit log for a document.

    Returns a paginated list of audit log entries recording every create and
    update action on the document, including who performed the action and what
    changed.

    Args:
        id: Numeric paperless-ngx document ID.
        page: Page number to retrieve (1-based). Omit to retrieve the first page.
        page_size: Number of entries per page. Omit to use the server default.

    Returns:
        ListResult with count (total audit log entries for this document) and
        items (entries on the requested page). Each entry contains a timestamp,
        action type, changes dict, and the actor who performed the action.
    """
    client = get_client()
    paged = client.documents.history(id, page=page, page_size=page_size)
    return ListResult(count=paged.count, items=paged.results)
