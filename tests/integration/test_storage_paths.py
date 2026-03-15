"""Integration tests for storage paths tools against a live paperless-ngx instance."""

import pytest
from easypaperless import StoragePath, SyncPaperlessClient

from easypaperless_mcp.tools.storage_paths import (
    bulk_delete_storage_paths,
    create_storage_path,
    delete_storage_path,
    get_storage_path,
    list_storage_paths,
    update_storage_path,
)


pytestmark = pytest.mark.integration

_TEST_NAME = "easypaperless-mcp integration test storage path"


@pytest.fixture(scope="module")
def existing_storage_path_id(paperless_client: SyncPaperlessClient) -> int:
    """Return the ID of the first available storage path, skipping if none exist."""
    paths = list_storage_paths()
    if not paths:
        pytest.skip("No storage paths in test instance")
    assert paths[0].id is not None
    return paths[0].id


# ---------------------------------------------------------------------------
# list_storage_paths
# ---------------------------------------------------------------------------


def test_list_storage_paths_returns_list(paperless_client: SyncPaperlessClient) -> None:
    result = list_storage_paths()
    assert isinstance(result, list)


def test_list_storage_paths_returns_storage_path_objects(paperless_client: SyncPaperlessClient) -> None:
    result = list_storage_paths()
    for sp in result:
        assert isinstance(sp, StoragePath)


def test_list_storage_paths_with_name_contains(paperless_client: SyncPaperlessClient) -> None:
    result = list_storage_paths(name_contains="")
    assert isinstance(result, list)


def test_list_storage_paths_with_path_contains(paperless_client: SyncPaperlessClient) -> None:
    result = list_storage_paths(path_contains="")
    assert isinstance(result, list)


# ---------------------------------------------------------------------------
# get_storage_path
# ---------------------------------------------------------------------------


def test_get_storage_path_returns_storage_path(
    paperless_client: SyncPaperlessClient, existing_storage_path_id: int
) -> None:
    result = get_storage_path(existing_storage_path_id)
    assert isinstance(result, StoragePath)
    assert result.id == existing_storage_path_id


# ---------------------------------------------------------------------------
# create / update / delete round trip
# ---------------------------------------------------------------------------


def test_create_update_delete_storage_path_round_trip(paperless_client: SyncPaperlessClient) -> None:
    """Create a storage path, update its name, verify the change, then delete it."""
    created = create_storage_path(name=_TEST_NAME, path="{title}")
    assert isinstance(created, StoragePath)
    assert created.name == _TEST_NAME
    assert created.id is not None

    try:
        updated = update_storage_path(created.id, name=_TEST_NAME + " updated")
        assert isinstance(updated, StoragePath)
        assert updated.name == _TEST_NAME + " updated"

        fetched = get_storage_path(created.id)
        assert fetched.name == _TEST_NAME + " updated"
    finally:
        delete_storage_path(created.id)

    remaining = [sp for sp in list_storage_paths() if sp.id == created.id]
    assert remaining == []


def test_bulk_delete_storage_paths_round_trip(paperless_client: SyncPaperlessClient) -> None:
    """Create two storage paths and bulk-delete them."""
    a = create_storage_path(name=_TEST_NAME + " bulk A", path="{title}")
    b = create_storage_path(name=_TEST_NAME + " bulk B", path="{title}")
    assert a.id is not None
    assert b.id is not None

    bulk_delete_storage_paths([a.id, b.id])

    remaining_ids = {sp.id for sp in list_storage_paths()}
    assert a.id not in remaining_ids
    assert b.id not in remaining_ids
