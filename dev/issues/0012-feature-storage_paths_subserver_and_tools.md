# [FEATURE] Storage paths sub-server with full resource tool coverage

## Summary

Implement a dedicated MCP sub-server for the storage paths resource, exposing all methods and parameters from `easypaperless` `SyncStoragePathsResource` as MCP tools. This enables AI agents to fully manage storage paths in paperless-ngx — listing, creating, updating, deleting, and bulk-operating on storage paths.

---

## Problem Statement

The storage paths resource is not yet exposed through the MCP server. AI agents cannot list existing storage paths, create new ones, update their properties (including auto-matching rules and path templates), or delete them. This gap prevents AI agents from managing the storage path configuration needed to control where paperless-ngx archives documents on disk.

---

## Proposed Solution

Create `src/easypaperless_mcp/tools/storage_paths.py` as a dedicated FastMCP sub-server, implementing all methods of `client.storage_paths` (`SyncStoragePathsResource`) as MCP tools. Mount the sub-server without namespace in `server.py`, following the same pattern used for the correspondents and document types sub-servers.

---

## User Stories

- As an AI agent, I want to list all storage paths (with optional name/path filters and pagination) so that I can discover which storage paths exist before assigning one to a document.
- As an AI agent, I want to get a single storage path by ID so that I can inspect its path template and matching rules.
- As an AI agent, I want to create a storage path with a name, path template, and matching rules so that I can define where documents should be stored.
- As an AI agent, I want to update an existing storage path so that I can correct its name, path template, or matching behaviour.
- As an AI agent, I want to delete a single storage path or bulk-delete multiple storage paths so that I can clean up unused paths.
- As an AI agent, I want to bulk-set permissions on multiple storage paths so that I can manage access control efficiently.

---

## Scope

### In Scope

- Create `src/easypaperless_mcp/tools/storage_paths.py` with its own `FastMCP` sub-server instance
- Mount the storage paths sub-server without namespace in `server.py`
- Implement the following MCP tools with all parameters from the sync methods overview:
  - `list_storage_paths` — parameters: `ids`, `name_contains`, `name_exact`, `path_contains`, `path_exact`, `page`, `page_size`, `ordering`, `descending`
  - `get_storage_path` — parameter: `id`
  - `create_storage_path` — parameters: `name`, `path`, `match`, `matching_algorithm`, `is_insensitive`, `owner`, `set_permissions`
  - `update_storage_path` — parameters: `id`, `name`, `path`, `match`, `matching_algorithm`, `is_insensitive`, `owner`, `set_permissions`
  - `delete_storage_path` — parameter: `id`
  - `bulk_delete_storage_paths` — parameter: `ids`
  - `bulk_set_storage_path_permissions` — parameters: `ids`, `set_permissions`, `owner`, `merge`
- Return types: `list_storage_paths` → `List[StoragePath]`; `get_storage_path`, `create_storage_path`, `update_storage_path` → `StoragePath`; delete/bulk tools → `None`
- Tool names follow verb-first, singular/plural cardinality convention from CLAUDE.md
- UNSET sentinel used for all optional `update_storage_path` parameters; `None` clears the field, omitting leaves it unchanged

### Out of Scope

- Changes to any other existing sub-server or resource
- Changes to transport configuration

---

## Acceptance Criteria

- [ ] `tools/storage_paths.py` exists and defines a `FastMCP` sub-server instance
- [ ] `server.py` mounts the storage paths sub-server without namespace alongside the existing sub-servers
- [ ] `list_storage_paths` is implemented with all 9 parameters (`ids`, `name_contains`, `name_exact`, `path_contains`, `path_exact`, `page`, `page_size`, `ordering`, `descending`) and returns `List[StoragePath]`
- [ ] `get_storage_path` is implemented with parameter `id` and returns `StoragePath`
- [ ] `create_storage_path` is implemented with all 7 parameters (`name`, `path`, `match`, `matching_algorithm`, `is_insensitive`, `owner`, `set_permissions`) and returns `StoragePath`
- [ ] `update_storage_path` is implemented with all 8 parameters (`id` + the same 7 as create, minus required `name`) using UNSET sentinel for all optional params so that `None` clears and omitting leaves unchanged; returns `StoragePath`
- [ ] `delete_storage_path` is implemented with parameter `id` and returns `None`
- [ ] `bulk_delete_storage_paths` is implemented with parameter `ids: List[int]` and returns `None`
- [ ] `bulk_set_storage_path_permissions` is implemented with parameters `ids`, `set_permissions`, `owner`, `merge` and returns `None`
- [ ] All 7 tools are registered and callable via the MCP server
- [ ] Tool names follow verb-first, singular/plural cardinality convention
- [ ] Return types use easypaperless Pydantic models directly (`StoragePath`)
- [ ] UNSET sentinel is used correctly for optional update parameters (distinguishes "not provided" from `None`)

---

## Dependencies & Constraints

- Depends on `easypaperless` package exposing all listed methods on `SyncPaperlessClient.storage_paths`
- `MatchingAlgorithm` and `SetPermissions` types must be imported from `easypaperless` as needed
- UNSET sentinel must be used for `update_storage_path` parameters that support leave-unchanged semantics

---

## Priority

`High`

---

## Additional Notes

- easypaperless storage paths API reference: https://moritzgrenke.github.io/easypaperless/easypaperless/resources.html
- Pattern to follow: `tools/document_types.py` and issue 0010
- `MatchingAlgorithm` enum values: `NONE | ANY_WORD | ALL_WORDS | EXACT | REGEX | FUZZY | AUTO`
- `list_storage_paths` has two extra filters compared to other resources: `path_contains` and `path_exact`
- `create_storage_path` and `update_storage_path` have an extra `path` parameter (the archive file path template); it is nullable — `None` clears it in update

---

## QA

**Tested by:** QA Engineer
**Date:** 2026-03-15
**Commit:** 649f3bc

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC: `tools/storage_paths.py` exists and defines a `FastMCP` sub-server instance | File exists, `storage_paths = FastMCP("storage_paths")` | Confirmed | ✅ Pass |
| 2 | AC: `server.py` mounts the sub-server without namespace | `mcp.mount(storage_paths)` added | Confirmed | ✅ Pass |
| 3 | AC: `list_storage_paths` with all 9 parameters, returns `List[StoragePath]` | 9 params present, correct return type | All 9 params present | ✅ Pass |
| 4 | AC: `get_storage_path(id)` returns `StoragePath` | Correct signature and return type | Confirmed | ✅ Pass |
| 5 | AC: `create_storage_path` with all 7 parameters, returns `StoragePath` | 7 params present | 7 params present, `path` is required (non-optional) | ✅ Pass |
| 6 | AC: `update_storage_path` uses UNSET sentinel for optional params; `None` clears; omit leaves unchanged | UNSET as default, None forwarded to client | Implemented correctly | ✅ Pass |
| 7 | AC: `delete_storage_path(id)` returns `None` | Correct signature | Confirmed | ✅ Pass |
| 8 | AC: `bulk_delete_storage_paths(ids)` returns `None` | Correct signature | Confirmed | ✅ Pass |
| 9 | AC: `bulk_set_storage_path_permissions` with 4 params, returns `None` | 4 params present | Confirmed | ✅ Pass |
| 10 | AC: All 7 tools registered and callable | All 7 tools present via `@storage_paths.tool` | Confirmed | ✅ Pass |
| 11 | AC: Verb-first naming convention | `list_`, `get_`, `create_`, `update_`, `delete_`, `bulk_delete_`, `bulk_set_` | All names correct | ✅ Pass |
| 12 | AC: Return types use easypaperless Pydantic models directly | `StoragePath` returned directly | Confirmed | ✅ Pass |
| 13 | AC: UNSET sentinel used correctly for update params | `_UNSET: Any = UNSET` used as default, compared with `is not UNSET` | Implemented | ✅ Pass |
| 14 | Integration: `create_storage_path(name=..., path="{title}")` succeeds | Storage path created, returns `StoragePath` | Passes | ✅ Pass |
| 15 | Integration: create+update+delete round-trip | Creates, updates name, fetch verifies, delete removes | Passes | ✅ Pass |
| 16 | Integration: bulk-delete round-trip | Create 2 paths, bulk-delete, verify gone | Passes (both calls include `path="{title}"`) | ✅ Pass |

### Bugs Found

(none)

### Automated Tests

- Unit suite (`tests/unit/test_storage_paths.py`): **33 passed, 0 failed**
- Integration suite (`tests/integration/test_storage_paths.py`): **7 passed, 0 failed**
- mypy (`--strict` on `storage_paths.py`): **9 errors** — pre-existing patterns shared by `correspondents.py`, `document_types.py`, etc. (untyped `dict` literals and UNSET identity-check overlap warnings). Not new regressions.
- ruff check: **0 violations**
- ruff format: **1 file would be reformatted** — pre-existing across other modules (same state as `correspondents.py`, `document_types.py`)

### Summary

- ACs tested: 13/13
- ACs passing: 13/13
- Bugs found: 0 (Critical: 0, High: 0, Medium: 0, Low: 0)
- Recommendation: ✅ Ready to merge
