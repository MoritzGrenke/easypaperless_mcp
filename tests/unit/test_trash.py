"""Unit tests for trash sub-server tools."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from easypaperless import Document

from easypaperless_mcp.tools.trash import (
    empty_trash,
    list_trash,
    restore_trash,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def patch_trash_get_client(patch_get_client: MagicMock):
    """Also patch get_client inside the trash module."""
    with patch("easypaperless_mcp.tools.trash.get_client", return_value=patch_get_client):
        yield patch_get_client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_document(**kwargs: Any) -> Document:
    """Build a minimal Document with sensible defaults."""
    defaults: dict[str, Any] = {
        "id": 1,
        "title": "Test Document",
        "created": "2024-01-01",
        "correspondent": None,
        "document_type": None,
        "storage_path": None,
        "tags": [],
        "custom_fields": [],
        "notes": [],
        "archive_serial_number": None,
        "original_file_name": "test.pdf",
        "content": "some content",
        "added": "2024-01-01",
        "modified": "2024-01-01",
    }
    defaults.update(kwargs)
    return Document.model_validate(defaults)


# ---------------------------------------------------------------------------
# list_trash
# ---------------------------------------------------------------------------


def test_list_trash_calls_client(patch_get_client: MagicMock) -> None:
    patch_get_client.trash.list.return_value = MagicMock(count=2, results=[make_document(id=1), make_document(id=2)])
    result = list_trash()
    patch_get_client.trash.list.assert_called_once()
    assert result.count == 2
    assert len(result.items) == 2


def test_list_trash_returns_empty(patch_get_client: MagicMock) -> None:
    patch_get_client.trash.list.return_value = MagicMock(count=0, results=[])
    result = list_trash()
    assert result.count == 0
    assert result.items == []


def test_list_trash_passes_page(patch_get_client: MagicMock) -> None:
    patch_get_client.trash.list.return_value = MagicMock(count=0, results=[])
    list_trash(page=2)
    assert patch_get_client.trash.list.call_args.kwargs["page"] == 2


def test_list_trash_passes_page_size(patch_get_client: MagicMock) -> None:
    patch_get_client.trash.list.return_value = MagicMock(count=0, results=[])
    list_trash(page_size=10)
    assert patch_get_client.trash.list.call_args.kwargs["page_size"] == 10


def test_list_trash_omits_none_params(patch_get_client: MagicMock) -> None:
    patch_get_client.trash.list.return_value = MagicMock(count=0, results=[])
    list_trash()
    call_kwargs = patch_get_client.trash.list.call_args.kwargs
    assert "page" not in call_kwargs
    assert "page_size" not in call_kwargs


def test_list_trash_returns_document_objects(patch_get_client: MagicMock) -> None:
    doc = make_document(id=5, title="Trashed Doc")
    patch_get_client.trash.list.return_value = MagicMock(count=1, results=[doc])
    result = list_trash()
    assert isinstance(result.items[0], Document)
    assert result.items[0].id == 5
    assert result.items[0].title == "Trashed Doc"


def test_list_trash_passes_page_and_page_size_together(patch_get_client: MagicMock) -> None:
    patch_get_client.trash.list.return_value = MagicMock(count=0, results=[])
    list_trash(page=3, page_size=25)
    call_kwargs = patch_get_client.trash.list.call_args.kwargs
    assert call_kwargs["page"] == 3
    assert call_kwargs["page_size"] == 25


def test_list_trash_returns_list_result_type(patch_get_client: MagicMock) -> None:
    from easypaperless_mcp.tools.models import ListResult

    patch_get_client.trash.list.return_value = MagicMock(count=0, results=[])
    result = list_trash()
    assert isinstance(result, ListResult)


# ---------------------------------------------------------------------------
# restore_trash
# ---------------------------------------------------------------------------


def test_restore_trash_calls_client(patch_get_client: MagicMock) -> None:
    restore_trash([1, 2, 3])
    patch_get_client.trash.restore.assert_called_once_with([1, 2, 3])


def test_restore_trash_returns_none(patch_get_client: MagicMock) -> None:
    patch_get_client.trash.restore.return_value = None
    result = restore_trash([1])
    assert result is None


def test_restore_trash_single_id(patch_get_client: MagicMock) -> None:
    restore_trash([42])
    patch_get_client.trash.restore.assert_called_once_with([42])


def test_restore_trash_empty_list(patch_get_client: MagicMock) -> None:
    restore_trash([])
    patch_get_client.trash.restore.assert_called_once_with([])


# ---------------------------------------------------------------------------
# empty_trash
# ---------------------------------------------------------------------------


def test_empty_trash_calls_client(patch_get_client: MagicMock) -> None:
    empty_trash([1, 2])
    patch_get_client.trash.empty.assert_called_once_with([1, 2])


def test_empty_trash_returns_none(patch_get_client: MagicMock) -> None:
    patch_get_client.trash.empty.return_value = None
    result = empty_trash([1])
    assert result is None


def test_empty_trash_single_id(patch_get_client: MagicMock) -> None:
    empty_trash([99])
    patch_get_client.trash.empty.assert_called_once_with([99])


def test_empty_trash_empty_list(patch_get_client: MagicMock) -> None:
    empty_trash([])
    patch_get_client.trash.empty.assert_called_once_with([])
