"""Unit tests for permission-based tool filtering (issue 0023)."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from easypaperless.models.users import User

from easypaperless_mcp.permissions import (
    TOOL_PERMISSIONS,
    filter_tools_by_permissions,
    get_effective_permissions,
)
from easypaperless_mcp.server import PermissionMiddleware, _SESSION_PERM_KEY


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_tool(name: str) -> MagicMock:
    t = MagicMock()
    t.name = name
    return t


def _make_user(**kwargs: Any) -> User:
    defaults: dict[str, Any] = {
        "id": 1,
        "username": "testuser",
        "user_permissions": [],
        "inherited_permissions": [],
        "is_superuser": False,
    }
    defaults.update(kwargs)
    return User.model_validate(defaults)


# ---------------------------------------------------------------------------
# TOOL_PERMISSIONS completeness
# ---------------------------------------------------------------------------

_EXPECTED_TOOLS = {
    # documents
    "list_documents",
    "get_document",
    "get_document_metadata",
    "update_document",
    "delete_document",
    "upload_document",
    "bulk_add_tag",
    "bulk_remove_tag",
    "bulk_modify_tags",
    "bulk_delete_documents",
    "bulk_set_correspondent",
    "bulk_set_document_type",
    "bulk_set_storage_path",
    "bulk_modify_custom_fields",
    "bulk_set_permissions",
    # document history
    "get_document_history",
    # document notes
    "list_document_notes",
    "create_document_note",
    "delete_document_note",
    # tags
    "list_tags",
    "get_tag",
    "create_tag",
    "update_tag",
    "delete_tag",
    "bulk_delete_tags",
    "bulk_set_tag_permissions",
    # correspondents
    "list_correspondents",
    "get_correspondent",
    "create_correspondent",
    "update_correspondent",
    "delete_correspondent",
    "bulk_delete_correspondents",
    "bulk_set_correspondent_permissions",
    # document types
    "list_document_types",
    "get_document_type",
    "create_document_type",
    "update_document_type",
    "delete_document_type",
    "bulk_delete_document_types",
    "bulk_set_document_type_permissions",
    # custom fields
    "list_custom_fields",
    "get_custom_field",
    "create_custom_field",
    "update_custom_field",
    "delete_custom_field",
    # storage paths
    "list_storage_paths",
    "get_storage_path",
    "create_storage_path",
    "update_storage_path",
    "delete_storage_path",
    "bulk_delete_storage_paths",
    "bulk_set_storage_path_permissions",
    # users
    "list_users",
    "get_user",
    "create_user",
    "update_user",
    "delete_user",
    # trash
    "list_trash",
    "restore_trash",
    "empty_trash",
}


def test_tool_permissions_covers_all_tools() -> None:
    assert set(TOOL_PERMISSIONS.keys()) == _EXPECTED_TOOLS


def test_tool_permissions_values_are_valid_permission_strings() -> None:
    for tool_name, perm in TOOL_PERMISSIONS.items():
        assert "." in perm, f"Permission for {tool_name!r} must be '<app>.<codename>': {perm!r}"


# ---------------------------------------------------------------------------
# get_effective_permissions
# ---------------------------------------------------------------------------


def test_get_effective_permissions_combines_user_and_inherited() -> None:
    user = _make_user(
        user_permissions=["documents.view_document"],
        inherited_permissions=["documents.change_document"],
    )
    result = get_effective_permissions(user)
    assert result == {"documents.view_document", "documents.change_document"}


def test_get_effective_permissions_deduplicates() -> None:
    user = _make_user(
        user_permissions=["documents.view_document"],
        inherited_permissions=["documents.view_document", "documents.add_document"],
    )
    result = get_effective_permissions(user)
    assert result == {"documents.view_document", "documents.add_document"}


def test_get_effective_permissions_none_fields() -> None:
    user = _make_user(user_permissions=None, inherited_permissions=None)
    assert get_effective_permissions(user) == set()


def test_get_effective_permissions_empty_lists() -> None:
    user = _make_user(user_permissions=[], inherited_permissions=[])
    assert get_effective_permissions(user) == set()


# ---------------------------------------------------------------------------
# filter_tools_by_permissions
# ---------------------------------------------------------------------------


def test_filter_allows_tools_with_required_permission() -> None:
    tools = [_make_tool("list_documents"), _make_tool("delete_document")]
    perms = {"documents.view_document", "documents.delete_document"}
    result = filter_tools_by_permissions(tools, perms)
    assert [t.name for t in result] == ["list_documents", "delete_document"]


def test_filter_hides_tools_without_required_permission() -> None:
    tools = [_make_tool("list_documents"), _make_tool("delete_document")]
    perms = {"documents.view_document"}
    result = filter_tools_by_permissions(tools, perms)
    assert [t.name for t in result] == ["list_documents"]


def test_filter_includes_unknown_tools_always() -> None:
    tools = [_make_tool("unknown_tool"), _make_tool("list_documents")]
    perms = {"documents.view_document"}
    result = filter_tools_by_permissions(tools, perms)
    assert {t.name for t in result} == {"unknown_tool", "list_documents"}


def test_filter_empty_permissions_hides_all_known_tools() -> None:
    tools = [_make_tool("list_documents"), _make_tool("create_tag")]
    result = filter_tools_by_permissions(tools, set())
    assert result == []


# ---------------------------------------------------------------------------
# PermissionMiddleware.on_list_tools
# ---------------------------------------------------------------------------


def _make_middleware_context(ctx: Any) -> MagicMock:
    context = MagicMock()
    context.fastmcp_context = ctx
    return context


def _all_tools() -> list[MagicMock]:
    return [_make_tool("list_documents"), _make_tool("delete_document"), _make_tool("create_tag")]


@pytest.fixture
def middleware() -> PermissionMiddleware:
    return PermissionMiddleware()


@pytest.fixture
def call_next_returning(request: Any) -> AsyncMock:
    tools = request.param if hasattr(request, "param") else _all_tools()
    mock = AsyncMock(return_value=tools)
    return mock


# --- No username supplied: all tools shown, no API call ---


@pytest.mark.asyncio
async def test_no_username_stdio_shows_all_tools(
    middleware: PermissionMiddleware, monkeypatch: Any
) -> None:
    monkeypatch.delenv("PAPERLESS_USERNAME", raising=False)
    monkeypatch.setenv("PAPERLESS_TOKEN", "tok")
    monkeypatch.setenv("PAPERLESS_URL", "http://x")

    all_tools = _all_tools()
    call_next = AsyncMock(return_value=all_tools)

    ctx = AsyncMock()
    ctx.get_state = AsyncMock(return_value=None)
    ctx.set_state = AsyncMock()

    transport_mock = MagicMock()
    transport_mock.get.return_value = "stdio"
    context = _make_middleware_context(ctx)

    with patch("fastmcp.server.context._current_transport", transport_mock):
        result = await middleware.on_list_tools(context, call_next)

    assert list(result) == all_tools
    ctx.set_state.assert_called_once_with(_SESSION_PERM_KEY, {"show_all": True, "perms": []})


@pytest.mark.asyncio
async def test_no_username_http_shows_all_tools(middleware: PermissionMiddleware) -> None:
    all_tools = _all_tools()
    call_next = AsyncMock(return_value=all_tools)

    ctx = AsyncMock()
    ctx.get_state = AsyncMock(return_value=None)
    ctx.set_state = AsyncMock()

    request = MagicMock()
    request.headers.get = lambda key, default=None: {
        "x-paperless-token": "tok",
        "x-paperless-url": "http://x",
    }.get(key, default)

    transport_mock = MagicMock()
    transport_mock.get.return_value = "http"
    context = _make_middleware_context(ctx)

    with (
        patch("fastmcp.server.context._current_transport", transport_mock),
        patch("fastmcp.server.dependencies.get_http_request", return_value=request),
        patch("easypaperless_mcp.server.SERVER_URL", None),
    ):
        result = await middleware.on_list_tools(context, call_next)

    assert list(result) == all_tools
    ctx.set_state.assert_called_once_with(_SESSION_PERM_KEY, {"show_all": True, "perms": []})


# --- Full-permissions user ---


@pytest.mark.asyncio
async def test_full_permissions_user_sees_all_tools(
    middleware: PermissionMiddleware, monkeypatch: Any
) -> None:
    monkeypatch.setenv("PAPERLESS_USERNAME", "alice")
    monkeypatch.setenv("PAPERLESS_TOKEN", "tok")
    monkeypatch.setenv("PAPERLESS_URL", "http://x")

    all_tools = _all_tools()
    all_perms = set(TOOL_PERMISSIONS.values())
    call_next = AsyncMock(return_value=all_tools)

    ctx = AsyncMock()
    ctx.get_state = AsyncMock(return_value=None)
    ctx.set_state = AsyncMock()

    user = _make_user(
        username="alice",
        is_superuser=False,
        user_permissions=list(all_perms),
        inherited_permissions=[],
    )
    paged = MagicMock()
    paged.results = [user]

    transport_mock = MagicMock()
    transport_mock.get.return_value = "stdio"
    context = _make_middleware_context(ctx)

    mock_client = AsyncMock()
    mock_client.users.list = AsyncMock(return_value=paged)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with (
        patch("fastmcp.server.context._current_transport", transport_mock),
        patch("easypaperless.client.PaperlessClient", return_value=mock_client),
    ):
        result = await middleware.on_list_tools(context, call_next)

    assert {t.name for t in result} == {t.name for t in all_tools}


# --- Read-only user: only view tools shown ---


@pytest.mark.asyncio
async def test_read_only_user_sees_only_view_tools(
    middleware: PermissionMiddleware, monkeypatch: Any
) -> None:
    monkeypatch.setenv("PAPERLESS_USERNAME", "bob")
    monkeypatch.setenv("PAPERLESS_TOKEN", "tok")
    monkeypatch.setenv("PAPERLESS_URL", "http://x")

    all_tools = _all_tools()  # list_documents, delete_document, create_tag
    call_next = AsyncMock(return_value=all_tools)

    ctx = AsyncMock()
    ctx.get_state = AsyncMock(return_value=None)
    ctx.set_state = AsyncMock()

    user = _make_user(
        username="bob",
        is_superuser=False,
        user_permissions=["documents.view_document", "documents.view_tag"],
        inherited_permissions=[],
    )
    paged = MagicMock()
    paged.results = [user]

    transport_mock = MagicMock()
    transport_mock.get.return_value = "stdio"
    context = _make_middleware_context(ctx)

    mock_client = AsyncMock()
    mock_client.users.list = AsyncMock(return_value=paged)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with (
        patch("fastmcp.server.context._current_transport", transport_mock),
        patch("easypaperless.client.PaperlessClient", return_value=mock_client),
    ):
        result = await middleware.on_list_tools(context, call_next)

    result_names = {t.name for t in result}
    assert "list_documents" in result_names
    assert "delete_document" not in result_names
    assert "create_tag" not in result_names


# --- Superuser bypass ---


@pytest.mark.asyncio
async def test_superuser_sees_all_tools(middleware: PermissionMiddleware, monkeypatch: Any) -> None:
    monkeypatch.setenv("PAPERLESS_USERNAME", "admin")
    monkeypatch.setenv("PAPERLESS_TOKEN", "tok")
    monkeypatch.setenv("PAPERLESS_URL", "http://x")

    all_tools = _all_tools()
    call_next = AsyncMock(return_value=all_tools)

    ctx = AsyncMock()
    ctx.get_state = AsyncMock(return_value=None)
    ctx.set_state = AsyncMock()

    user = _make_user(
        username="admin",
        is_superuser=True,
        user_permissions=[],
        inherited_permissions=[],
    )
    paged = MagicMock()
    paged.results = [user]

    transport_mock = MagicMock()
    transport_mock.get.return_value = "stdio"
    context = _make_middleware_context(ctx)

    mock_client = AsyncMock()
    mock_client.users.list = AsyncMock(return_value=paged)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with (
        patch("fastmcp.server.context._current_transport", transport_mock),
        patch("easypaperless.client.PaperlessClient", return_value=mock_client),
    ):
        result = await middleware.on_list_tools(context, call_next)

    assert list(result) == all_tools
    ctx.set_state.assert_called_once_with(_SESSION_PERM_KEY, {"show_all": True, "perms": []})


# --- Lookup failure ---


@pytest.mark.asyncio
async def test_user_not_found_raises_error(
    middleware: PermissionMiddleware, monkeypatch: Any
) -> None:
    monkeypatch.setenv("PAPERLESS_USERNAME", "ghost")
    monkeypatch.setenv("PAPERLESS_TOKEN", "tok")
    monkeypatch.setenv("PAPERLESS_URL", "http://x")

    call_next = AsyncMock(return_value=_all_tools())

    ctx = AsyncMock()
    ctx.get_state = AsyncMock(return_value=None)
    ctx.set_state = AsyncMock()

    paged = MagicMock()
    paged.results = []

    transport_mock = MagicMock()
    transport_mock.get.return_value = "stdio"
    context = _make_middleware_context(ctx)

    mock_client = AsyncMock()
    mock_client.users.list = AsyncMock(return_value=paged)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with (
        patch("fastmcp.server.context._current_transport", transport_mock),
        patch("easypaperless.client.PaperlessClient", return_value=mock_client),
    ):
        with pytest.raises(RuntimeError, match="not found"):
            await middleware.on_list_tools(context, call_next)


@pytest.mark.asyncio
async def test_api_error_raises_descriptive_error(
    middleware: PermissionMiddleware, monkeypatch: Any
) -> None:
    monkeypatch.setenv("PAPERLESS_USERNAME", "alice")
    monkeypatch.setenv("PAPERLESS_TOKEN", "tok")
    monkeypatch.setenv("PAPERLESS_URL", "http://x")

    call_next = AsyncMock(return_value=_all_tools())

    ctx = AsyncMock()
    ctx.get_state = AsyncMock(return_value=None)
    ctx.set_state = AsyncMock()

    transport_mock = MagicMock()
    transport_mock.get.return_value = "stdio"
    context = _make_middleware_context(ctx)

    mock_client = AsyncMock()
    mock_client.users.list = AsyncMock(side_effect=Exception("connection refused"))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with (
        patch("fastmcp.server.context._current_transport", transport_mock),
        patch("easypaperless.client.PaperlessClient", return_value=mock_client),
    ):
        with pytest.raises(RuntimeError, match="Permission lookup failed"):
            await middleware.on_list_tools(context, call_next)


# --- Cache hit: lookup called only once per session ---


@pytest.mark.asyncio
async def test_cache_hit_skips_api_call(middleware: PermissionMiddleware, monkeypatch: Any) -> None:
    monkeypatch.setenv("PAPERLESS_USERNAME", "alice")

    all_tools = _all_tools()
    call_next = AsyncMock(return_value=all_tools)

    # Pre-populated cache: read-only permissions
    cached_perms = {"documents.view_document"}
    cached_state: dict[str, object] = {"show_all": False, "perms": list(cached_perms)}

    ctx = AsyncMock()
    ctx.get_state = AsyncMock(return_value=cached_state)
    ctx.set_state = AsyncMock()

    transport_mock = MagicMock()
    transport_mock.get.return_value = "stdio"
    context = _make_middleware_context(ctx)

    with (
        patch("fastmcp.server.context._current_transport", transport_mock),
        patch("easypaperless.client.PaperlessClient") as mock_pc,
    ):
        result = await middleware.on_list_tools(context, call_next)

    # PaperlessClient must not be instantiated on a cache hit
    mock_pc.assert_not_called()
    result_names = {t.name for t in result}
    assert "list_documents" in result_names
    assert "delete_document" not in result_names


@pytest.mark.asyncio
async def test_cache_hit_show_all_returns_all_tools(middleware: PermissionMiddleware) -> None:
    all_tools = _all_tools()
    call_next = AsyncMock(return_value=all_tools)

    cached_state: dict[str, object] = {"show_all": True, "perms": []}

    ctx = AsyncMock()
    ctx.get_state = AsyncMock(return_value=cached_state)
    ctx.set_state = AsyncMock()

    transport_mock = MagicMock()
    transport_mock.get.return_value = "stdio"
    context = _make_middleware_context(ctx)

    with (
        patch("fastmcp.server.context._current_transport", transport_mock),
        patch("easypaperless.client.PaperlessClient") as mock_pc,
    ):
        result = await middleware.on_list_tools(context, call_next)

    mock_pc.assert_not_called()
    assert list(result) == all_tools


# --- No fastmcp_context: pass through ---


@pytest.mark.asyncio
async def test_no_fastmcp_context_passes_through(middleware: PermissionMiddleware) -> None:
    all_tools = _all_tools()
    call_next = AsyncMock(return_value=all_tools)
    context = _make_middleware_context(None)

    result = await middleware.on_list_tools(context, call_next)
    assert list(result) == all_tools
