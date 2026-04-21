"""Integration tests for documents tools against a live paperless-ngx instance."""

import pytest
from easypaperless import SyncPaperlessClient

from easypaperless_mcp.tools.documents import get_document, list_documents, update_document
from easypaperless_mcp.tools.models import ListResult


pytestmark = pytest.mark.integration


def test_list_documents_returns_list_result(paperless_client: SyncPaperlessClient) -> None:
    result = list_documents(max_results=5)
    assert isinstance(result, ListResult)
    assert isinstance(result.count, int)
    assert isinstance(result.items, list)


def test_list_documents_search(paperless_client: SyncPaperlessClient) -> None:
    result = list_documents(search="a", max_results=5)
    assert isinstance(result, ListResult)


def test_get_document_round_trip(paperless_client: SyncPaperlessClient) -> None:
    result = list_documents(max_results=1)
    if not result.items:
        pytest.skip("No documents in test instance")
    doc_id = result.items[0]["id"]
    assert doc_id is not None
    fetched = get_document(doc_id)
    assert fetched["id"] == doc_id


# ---------------------------------------------------------------------------
# add_tags / remove_tags (issue 0025)
# ---------------------------------------------------------------------------


def _get_test_doc_and_tag(paperless_client: SyncPaperlessClient) -> tuple[int, int, list[int]]:
    """Return (doc_id, tag_id, original_tags) or skip the test."""
    docs = list_documents(max_results=1)
    if not docs.items:
        pytest.skip("No documents in test instance")
    doc_id: int = docs.items[0]["id"]

    tags_page = paperless_client.tags.list()
    if not tags_page.results:
        pytest.skip("No tags in test instance")
    tag_id: int = tags_page.results[0].id  # type: ignore[assignment]

    current_doc = paperless_client.documents.get(id=doc_id)
    original_tags: list[int] = list(current_doc.tags)
    return doc_id, tag_id, original_tags


def test_update_document_add_tags_adds_to_existing(paperless_client: SyncPaperlessClient) -> None:
    doc_id, tag_id, original_tags = _get_test_doc_and_tag(paperless_client)
    # Ensure the tag is not already on the document so add is meaningful
    baseline = [t for t in original_tags if t != tag_id]
    paperless_client.documents.update(doc_id, tags=baseline)
    try:
        updated = update_document(doc_id, add_tags=[tag_id])
        assert tag_id in updated.tags
        # All pre-existing baseline tags are still present
        for t in baseline:
            assert t in updated.tags
    finally:
        paperless_client.documents.update(doc_id, tags=original_tags)


def test_update_document_remove_tags_removes_from_existing(paperless_client: SyncPaperlessClient) -> None:
    doc_id, tag_id, original_tags = _get_test_doc_and_tag(paperless_client)
    # Ensure the tag is on the document before removing
    with_tag = list({*original_tags, tag_id})
    paperless_client.documents.update(doc_id, tags=with_tag)
    try:
        updated = update_document(doc_id, remove_tags=[tag_id])
        assert tag_id not in updated.tags
    finally:
        paperless_client.documents.update(doc_id, tags=original_tags)


def test_update_document_add_and_remove_tags_combined(paperless_client: SyncPaperlessClient) -> None:
    """add_tags and remove_tags work together in a single call."""
    docs = list_documents(max_results=1)
    if not docs.items:
        pytest.skip("No documents in test instance")
    doc_id: int = docs.items[0]["id"]

    tags_page = paperless_client.tags.list()
    if len(tags_page.results) < 2:
        pytest.skip("Need at least 2 tags in test instance")

    tag_to_add: int = tags_page.results[0].id  # type: ignore[assignment]
    tag_to_remove: int = tags_page.results[1].id  # type: ignore[assignment]

    current_doc = paperless_client.documents.get(id=doc_id)
    original_tags: list[int] = list(current_doc.tags)

    # Set up: tag_to_remove present, tag_to_add absent
    baseline = list({*original_tags, tag_to_remove} - {tag_to_add})
    paperless_client.documents.update(doc_id, tags=baseline)
    try:
        updated = update_document(doc_id, add_tags=[tag_to_add], remove_tags=[tag_to_remove])
        assert tag_to_add in updated.tags
        assert tag_to_remove not in updated.tags
    finally:
        paperless_client.documents.update(doc_id, tags=original_tags)
