"""Trash sub-server: MCP tools for the paperless-ngx trash resource."""

from typing import Any

from easypaperless import Document
from fastmcp import FastMCP

from ..client import get_client
from .models import ListResult

trash = FastMCP("trash")


@trash.tool
def list_trash(
    page: int | None = None,
    page_size: int | None = None,
) -> ListResult[Document]:
    """List all documents currently in the paperless-ngx trash.

    When ``page`` is omitted, all trashed documents are fetched automatically
    across all pages.  When ``page`` is set, only that specific page is returned.

    Args:
        page: Page number for manual pagination (1-based).
        page_size: Number of results per page.

    Returns:
        ListResult with count (total trashed documents) and items (list of
        Document objects in the trash).
    """
    client = get_client()
    kwargs: dict[str, Any] = {}
    if page is not None:
        kwargs["page"] = page
    if page_size is not None:
        kwargs["page_size"] = page_size
    paged = client.trash.list(**kwargs)
    return ListResult(count=paged.count, items=paged.results)


@trash.tool
def restore_trash(document_ids: list[int]) -> None:
    """Restore trashed documents back to active status.

    Args:
        document_ids: List of numeric document IDs to restore from the trash.
    """
    client = get_client()
    client.trash.restore(document_ids)


@trash.tool
def empty_trash(document_ids: list[int]) -> None:
    """Permanently delete specific documents from the trash.

    .. warning::
        **This operation is irreversible and cannot be undone.**
        The specified documents will be permanently removed and cannot be
        recovered. Use ``list_trash`` first to confirm which documents to delete.

    Args:
        document_ids: List of numeric document IDs to permanently delete from
            the trash.
    """
    client = get_client()
    client.trash.empty(document_ids)
