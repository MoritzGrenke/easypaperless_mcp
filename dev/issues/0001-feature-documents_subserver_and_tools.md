# [FEATURE] Documents sub-server with full resource tool coverage

## Summary

Restructure the existing monolithic `server.py` into the proper layered architecture defined in CLAUDE.md, and deliver a complete MCP tool set for the documents resource. This replaces the current placeholder implementation with production-ready tools that cover every operation exposed by the `easypaperless` documents API — including bulk operations and field-filtered responses.

---

## Problem Statement

The current codebase has all logic in a single `server.py` with only three rudimentary tools (`list_documents`, `get_document`, `search_documents`). Two of those tools are duplicates of each other. The project structure defined in CLAUDE.md (separate `client.py`, `tools/` sub-servers per resource) has not been established yet. Without this foundation, the remaining resource modules cannot be added cleanly.

Additionally, the document tools return either only titles or full model dumps, providing no token-efficient middle ground for AI agents working with large document sets.

---

## Proposed Solution

Refactor the codebase to match the target project structure, then implement all methods of the `easypaperless` documents resource as MCP tools on a dedicated `tools/documents.py` sub-server.

The sub-server is mounted without namespace in `server.py`. A `client.py` module provides the `get_client()` singleton. The `search_documents` tool is removed as a duplicate.

Two tools (`list_documents`, `get_document`) receive a `return_fields` parameter that restricts which fields are included in the response — all other fields are set to `None` before returning — allowing AI agents to request only the data they need.

The `download` tool is explicitly excluded.

---

## User Stories

- As an AI agent, I want to list documents with only the fields I need so that I don't waste context window on irrelevant data.
- As an AI agent, I want to get detailed information about a single document with a configurable field selection so that I can retrieve richer data on demand.
- As an AI agent, I want to update, delete, upload, and manage metadata for individual documents so that I can maintain a paperless-ngx instance.
- As an AI agent, I want to perform bulk tag, correspondent, document type, storage path, custom field, and permission operations so that I can efficiently process large document collections.

---

## Scope

### In Scope

- Restructure: extract `get_client()` singleton into `src/easypaperless_mcp/client.py`
- Restructure: create `src/easypaperless_mcp/tools/__init__.py` (empty)
- Restructure: create `src/easypaperless_mcp/tools/documents.py` with its own `FastMCP` sub-server instance
- Restructure: update `server.py` to import and mount the documents sub-server; remove inline tool definitions and `get_client()`
- Remove: `search_documents` tool (duplicate of `list_documents`)
- Implement individual document tools:
  - `list_documents` — filters: title, content, tags, dates, correspondent, document type, storage path, ordering, search, max_results; `return_fields` parameter (see defaults below)
  - `get_document` — by ID; `return_fields` parameter (see defaults below)
  - `get_document_metadata` — file-level technical metadata (checksums, sizes, MIME types)
  - `update_document` — partial update via PATCH semantics; supports UNSET fields
  - `delete_document` — permanently remove a document
  - `upload_document` — upload a file; optionally wait for processing task completion
- Implement bulk document tools:
  - `bulk_add_tag`
  - `bulk_remove_tag`
  - `bulk_modify_tags`
  - `bulk_delete_documents`
  - `bulk_set_correspondent`
  - `bulk_set_document_type`
  - `bulk_set_storage_path`
  - `bulk_modify_custom_fields`
  - `bulk_set_permissions`
- `return_fields` for `list_documents` defaults to: `["id", "title", "created", "correspondent", "document_type", "tags", "archive_serial_number"]`
- `return_fields` for `get_document` defaults to: `["id", "title", "created", "correspondent", "document_type", "storage_path", "tags", "custom_fields", "notes", "archive_serial_number", "original_file_name", "page_count"]`
- Fields not listed in `return_fields` are set to `None` on the returned model before serialization

### Out of Scope

- `download_document` tool — not implemented by design
- Tools for any other resource (tags, correspondents, etc.) — separate issues
- Changes to transport configuration or environment variable handling

---

## Acceptance Criteria

- [ ] `client.py` exists and exports `get_client() -> SyncPaperlessClient`
- [ ] `tools/__init__.py` exists
- [ ] `tools/documents.py` defines a `FastMCP` sub-server instance and all tools listed above
- [ ] `server.py` mounts the documents sub-server without namespace and no longer contains inline tool definitions or `get_client()`
- [ ] `search_documents` tool is removed and no longer registered
- [ ] `list_documents` accepts a `return_fields: list[str]` parameter with the specified default; fields absent from the list are set to `None` on the returned document objects
- [ ] `get_document` accepts a `return_fields: list[str]` parameter with the specified default; fields absent from the list are set to `None` on the returned document object
- [ ] All 6 individual document tools (`list_documents`, `get_document`, `get_document_metadata`, `update_document`, `delete_document`, `upload_document`) are registered and callable
- [ ] All 9 bulk operation tools are registered and callable
- [ ] Tool names follow verb-first, singular/plural cardinality convention from CLAUDE.md
- [ ] Return types use easypaperless Pydantic models directly where meaningful
- [ ] No tool named `download_document` exists

---

## Dependencies & Constraints

- Depends on `easypaperless` package exposing all listed methods on `SyncPaperlessClient.documents`
- `return_fields` filtering must set non-listed fields to `None` (not omit them from the schema), so the Pydantic model remains valid and fully typed
- UNSET semantics for `update_document` must be handled in line with how `easypaperless` exposes them (likely a sentinel value)

---

## Priority

`High`

---

## Additional Notes

- easypaperless documents API reference: https://moritzgrenke.github.io/easypaperless/easypaperless/resources.html
- The `return_fields` mechanism is the primary context-saving measure described in the PRD. Keeping defaults narrow prevents accidental large responses from agents that do not explicitly request more fields.

---

## QA

**Tested by:** QA Engineer
**Date:** 2026-03-15
**Commit:** 9834663

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC: `client.py` exists and exports `get_client() -> SyncPaperlessClient` | File present, correct return type | Present at `src/easypaperless_mcp/client.py`; singleton pattern with env-var validation | ✅ Pass |
| 2 | AC: `tools/__init__.py` exists | File present (empty) | Present | ✅ Pass |
| 3 | AC: `tools/documents.py` defines FastMCP sub-server and all tools | All 15 tools registered | All 15 tools present (`list_documents`, `get_document`, `get_document_metadata`, `update_document`, `delete_document`, `upload_document`, 9 bulk tools) | ✅ Pass |
| 4 | AC: `server.py` mounts documents sub-server without namespace; no inline tools or `get_client()` | `mcp.mount(documents)` only | `mcp.mount(documents)` — no inline definitions, no `get_client()` | ✅ Pass |
| 5 | AC: `search_documents` removed | Not present anywhere in `src/` | Absent | ✅ Pass |
| 6 | AC: `list_documents` `return_fields` with correct default | `["id","title","created","correspondent","document_type","tags","archive_serial_number"]` | Matches spec exactly | ✅ Pass |
| 7 | AC: `get_document` `return_fields` with correct default | 11-field list including `notes`, `custom_fields`, `page_count` | Matches spec exactly | ✅ Pass |
| 8 | AC: All 6 individual document tools callable | All present and importable | All 6 present | ✅ Pass |
| 9 | AC: All 9 bulk tools callable | All present and importable | All 9 present | ✅ Pass |
| 10 | AC: Tool names follow verb-first naming convention | `list_`, `get_`, `update_`, `delete_`, `upload_`, `bulk_` prefixes | All tools follow convention | ✅ Pass |
| 11 | AC: Pydantic models returned directly | `Document`, `DocumentMetadata` etc. | All tools return easypaperless models | ✅ Pass |
| 12 | AC: No `download_document` tool | Absent | Not found in `src/` | ✅ Pass |
| 13 | AC: `return_fields` sets non-listed fields to `None` (not removes them) | `model_copy(update={field: None})` | `_filter_fields` uses `model_copy` correctly | ✅ Pass |
| 14 | Automated unit tests — all tools and `_filter_fields` | 57 tests pass | 57/57 passed | ✅ Pass |
| 15 | Ruff lint check (`src/`) | No errors | No errors in `src/` | ✅ Pass |
| 16 | Integration: live paperless-ngx smoke test | N/A | Untested — requires live paperless-ngx instance | ⚪ Skip |

### Bugs Found

#### BUG-001 — Unused import `_GET_RETURN_FIELDS` in test file [Severity: Low]
**Steps to reproduce:**
1. Run `ruff check tests/unit/test_documents.py`

**Expected:** No lint errors
**Actual:** `F401 _GET_RETURN_FIELDS imported but unused` at `tests/unit/test_documents.py:9`
**Severity:** Low
**Notes:** `_GET_RETURN_FIELDS` is imported but never referenced in any test assertion. Fixable with `--fix`.

#### BUG-002 — `ruff` and `mypy` not in dev dependencies [Severity: Low]
**Steps to reproduce:**
1. Create a fresh virtual environment from `pyproject.toml` dev extras: `uv sync --extra dev`
2. Try to run `ruff` or `mypy`

**Expected:** Both tools available after `uv sync --extra dev`
**Actual:** Neither is installed; they must be invoked via `uv tool run` without project package context
**Severity:** Low
**Notes:** `mypy` in particular cannot type-check the project when run outside the venv (import-not-found errors for `easypaperless` and `fastmcp`). Should be added to `[project.optional-dependencies].dev`.

### Automated Tests
- Suite: `tests/unit` — 57 passed, 0 failed
- No integration tests run (require live instance)

### Summary
- ACs tested: 12/12 (1 untested — integration, requires live infra)
- ACs passing: 12/12
- Bugs found: 2 (Critical: 0, High: 0, Medium: 0, Low: 2)
- Recommendation: ✅ Ready to merge
