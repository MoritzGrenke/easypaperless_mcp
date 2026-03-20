# [FEATURE] Trash sub-server with full resource tool coverage

## Summary

Add a `trash` sub-server to easypaperless-mcp that exposes the `TrashResource` from easypaperless 0.4.0, giving AI agents the ability to list trashed documents, restore them, and permanently empty the trash.

---

## Problem Statement

easypaperless 0.4.0 introduced a `TrashResource` for managing paperless-ngx's trash. This resource is not yet exposed as MCP tools, so AI agents cannot inspect, recover, or permanently discard trashed documents.

---

## Proposed Solution

Create `src/easypaperless_mcp/tools/trash.py` as a new FastMCP sub-server following the same conventions as the existing resource sub-servers (tags, correspondents, users, etc.). Mount it in `server.py`. Expose all three operations available in `SyncTrashResource`.

---

## User Stories

- As an AI agent, I want to list all trashed documents so that I can decide which ones to restore or permanently delete.
- As an AI agent, I want to restore one or more trashed documents so that I can recover accidentally deleted items.
- As an AI agent, I want to permanently empty the trash so that I can free space and clean up the instance.

---

## Scope

### In Scope
- `list_trash` tool — wraps `SyncTrashResource.list()`, returns `ListResult` with total count and results; supports `page` and `page_size` parameters
- `restore_trash` tool — wraps `SyncTrashResource.restore(ids)`, restores one or more documents by ID list
- `empty_trash` tool — wraps `SyncTrashResource.empty()`, permanently deletes all trashed items; tool docstring must warn that this action is irreversible
- Mount the new sub-server in `server.py` (no namespace, consistent with other sub-servers)

### Out of Scope
- Selectively deleting individual trashed items permanently (not supported by the easypaperless API)
- Any other resource types that may appear in trash (easypaperless only exposes document trash)

---

## Acceptance Criteria

- [ ] `src/easypaperless_mcp/tools/trash.py` exists and defines a `FastMCP` instance named `trash`
- [ ] `list_trash` returns a `ListResult` and supports `page` and `page_size` parameters
- [ ] `restore_trash(ids)` restores the specified documents and returns a confirmation; `ids` is a required list of integers
- [ ] `empty_trash()` permanently empties the trash and returns a confirmation; the docstring clearly warns the action is irreversible
- [ ] The `trash` sub-server is mounted in `server.py`
- [ ] All tools pass mypy strict checks and ruff linting
- [ ] Unit tests cover all three tools (happy path + edge cases)

---

## Dependencies & Constraints

- Requires easypaperless >= 0.4.0
- Tool parameter names must match easypaperless API names exactly (`ids`, `page`, `page_size`)
- `empty_trash` is a destructive, irreversible operation — the tool docstring must reflect this clearly

---

## Priority

`Medium`

---

## Additional Notes

- `SyncTrashResource` methods: `list(page=None, page_size=None)`, `restore(ids: list[int])`, `empty()`
- Reference implementation: `tools/users.py`, `tools/tags.py`

---

## QA

**Tested by:** QA Engineer
**Date:** 2026-03-20
**Commit:** 7c10c84

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC1: `trash.py` exists with `FastMCP` instance named `trash` | File exists, `trash = FastMCP("trash")` | ✅ Matches | ✅ Pass |
| 2 | AC2: `list_trash` returns `ListResult` with `page`/`page_size` params | `ListResult[Document]`, both params present | Returns `ListResult`, both params supported | ✅ Pass |
| 3 | AC3: `restore_trash(ids)` — param named `ids`, required `list[int]` | Parameter named `ids` | Parameter named `document_ids` (matches actual easypaperless API `restore(document_ids)`, but deviates from AC and constraints spec which say `ids`) | ❌ Fail |
| 4 | AC3: `restore_trash` returns a confirmation | Returns a confirmation string | Returns `None` | ❌ Fail |
| 5 | AC4: `empty_trash()` has no parameters per AC and scope ("permanently deletes all trashed items") | No parameters | Has `document_ids: list[int]` parameter (matches actual easypaperless API `empty(document_ids)`, but deviates from AC) | ❌ Fail |
| 6 | AC4: `empty_trash` returns a confirmation | Returns a confirmation string | Returns `None` | ❌ Fail |
| 7 | AC4: `empty_trash` docstring clearly warns irreversible | Warning present | `.. warning::` block with clear irreversibility warning | ✅ Pass |
| 8 | AC5: `trash` sub-server mounted in `server.py` | `mcp.mount(trash)` present | `mcp.mount(trash)` on line 76 | ✅ Pass |
| 9 | AC6: mypy strict passes | No mypy errors | `Success: no issues found` | ✅ Pass |
| 10 | AC6: ruff linting passes | No ruff errors | `All checks passed!` | ✅ Pass |
| 11 | AC7: Unit tests cover all three tools | Happy path + edge cases | 16 unit tests covering `list_trash`, `restore_trash`, `empty_trash` | ✅ Pass |
| 12 | Edge: `list_trash` omits `page`/`page_size` when not provided | Params not forwarded to client | Confirmed via `test_list_trash_omits_none_params` | ✅ Pass |
| 13 | Integration: `list_trash` against live instance | Returns `ListResult[Document]` | 3 integration tests pass against live paperless-ngx | ✅ Pass |

### Bugs Found

#### BUG-001 — `restore_trash` and `empty_trash` return `None` instead of a confirmation [Severity: Medium]
**Steps to reproduce:**
1. Call `restore_trash([1])` or `empty_trash([1])`
2. Observe the return value

**Expected:** A confirmation value (e.g. `"Restored 1 document(s)."` or similar string) as stated in AC3 and AC4.
**Actual:** Both tools return `None`.
**Severity:** Medium
**Notes:** Other destructive tools in the codebase (e.g. `delete_document`) also return `None`, so this is consistent with the broader pattern but still contradicts the explicit AC wording.

#### BUG-002 — Parameter naming deviates from spec constraints [Severity: Low]
**Steps to reproduce:**
1. Inspect `restore_trash` and `empty_trash` signatures in `trash.py`
2. Both use `document_ids` as the parameter name

**Expected:** Per AC3, constraints section ("Tool parameter names must match easypaperless API names exactly (`ids`, `page`, `page_size`)"), parameter should be named `ids`.
**Actual:** Parameter is named `document_ids`.
**Severity:** Low
**Notes:** This is a spec ambiguity — the actual installed easypaperless 0.4.0 package uses `document_ids` (not `ids`) for both `restore(document_ids)` and `empty(document_ids)`. The implementation correctly follows the real API, making the constraint in the spec incorrect. The AC and the Additional Notes are inconsistent with each other and with the real library. Recommend updating the spec to reflect the actual API rather than changing the implementation.

#### BUG-003 — `empty_trash` scope description contradicts actual implementation [Severity: Low]
**Steps to reproduce:**
1. Read Scope section: "`empty_trash` — wraps `SyncTrashResource.empty()`, permanently deletes **all** trashed items"
2. Read Additional Notes: `empty()` (no parameters)
3. Observe actual easypaperless 0.4.0 API: `empty(document_ids: List[int])` — selective, not all-at-once

**Expected per spec:** `empty_trash()` takes no parameters and permanently empties the entire trash.
**Actual:** `empty_trash(document_ids: list[int])` permanently deletes only the specified documents.
**Severity:** Low
**Notes:** The spec's out-of-scope note says "Selectively deleting individual trashed items permanently (not supported by the easypaperless API)" — but that is exactly what the actual easypaperless API supports via `empty(document_ids)`. The spec was written against incorrect assumptions about the upstream library. The implementation correctly reflects the real API behavior. No code change needed; the issue spec needs correction.

### Automated Tests
- Suite: unit/test_trash.py — 16 passed, 0 failed
- Suite: integration/test_trash.py — 3 passed, 0 failed
- Suite: full unit suite — 288 passed, 0 failed (no regressions)

### Summary
- ACs tested: 7/7
- ACs passing: 4/7
- Bugs found: 3 (Critical: 0, High: 0, Medium: 1, Low: 2)
- Recommendation: ❌ Needs fixes before merge — BUG-001 (missing confirmation return values) must be resolved; BUG-002 and BUG-003 are spec issues that can be resolved by updating the issue spec rather than changing code.
