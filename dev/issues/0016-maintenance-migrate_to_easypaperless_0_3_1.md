# [MAINTENANCE] Migrate easypaperless_mcp to easypaperless 0.3.1

## Summary

easypaperless 0.3.1 was installed. It fixes the HTTPS pagination bug (issue 0015) and restores the `PagedResult` return type for `documents.notes.list()`, which was accidentally omitted in 0.3.0. The MCP server must be updated to handle the new return type and the new parameters of that method.

---

## Background / Context

easypaperless 0.3.1 contains two changes relevant to easypaperless_mcp:

1. **Bug fix (issue 0015 resolved upstream):** Pagination `next` URLs are now scheme-normalised inside easypaperless, so HTTPS instances no longer fail when results span multiple pages. No changes required in easypaperless_mcp.

2. **Breaking change in `documents.notes.list()`:** In 0.3.0 this method returned `List[DocumentNote]` directly. In 0.3.1 it returns `PagedResult[DocumentNote]`, consistent with all other list methods. It also gained `page` and `page_size` parameters. The current `list_document_notes` tool passes the return value straight through as `list[DocumentNote]`, which will now break at runtime.

---

## Objectives

- Update `list_document_notes` to correctly unwrap the new `PagedResult[DocumentNote]` return value and expose pagination parameters.
- Keep the tool's return shape consistent with all other `list_*` tools (`ListResult[DocumentNote]`).
- Close out issue 0015 as resolved by the upstream fix.

---

## Scope

### In Scope
- Update `list_document_notes` in `tools/document_notes.py`:
  - Change return type from `list[DocumentNote]` to `ListResult[DocumentNote]`.
  - Unwrap `.results` and `.count` from the `PagedResult` returned by `client.documents.notes.list()`.
  - Add `page` and `page_size` parameters (consistent with all other list tools).
- Update affected unit tests in `tests/unit/test_document_notes.py`.
- Mark issue 0015 as `RESOLVED` in the issue index (fixed upstream in easypaperless 0.3.1).

### Out of Scope
- Any other tools or resources.
- Changes to MCP transport or server configuration.

---

## Acceptance Criteria
- [ ] `list_document_notes` returns `ListResult[DocumentNote]` with `count` and `items` fields.
- [ ] `list_document_notes` accepts optional `page` and `page_size` parameters and forwards them to `client.documents.notes.list()`.
- [ ] `list_document_notes` correctly unwraps `.results` and `.count` from the `PagedResult` response.
- [ ] All unit tests for `list_document_notes` pass and cover the updated return shape.
- [ ] `ruff check` passes with no errors.
- [ ] `mypy --strict` passes with no errors.
- [ ] All existing unit and integration tests pass.

---

## Dependencies

- easypaperless 0.3.1 must be installed (done).
- Related: issue 0013 (migration to 0.3.0), issue 0015 (resolved upstream).

---

## Priority
`High`

---

## Additional Notes

- The `SyncNotesResource.list()` signature in 0.3.1: `list(document_id: int, *, page: int | None = None, page_size: int | None = None) -> PagedResult[DocumentNote]`.
- `PagedResult[T]` fields: `.results` (list of items), `.count` (total), `.next`, `.previous`, `.all`.
- Issue 0015 status should be updated to `RESOLVED` in the index — the fix lives in easypaperless 0.3.1, not in this project.

---

## QA

**Tested by:** QA Engineer
**Date:** 2026-03-18
**Commit:** 4cb1d0f

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC1: `list_document_notes` returns `ListResult[DocumentNote]` with `count` and `items` | Tool returns `ListResult` wrapping `paged.count` / `paged.results` | Implemented correctly in `document_notes.py:31` | ✅ Pass (unit) / ❌ Fail (integration — upstream bug) |
| 2 | AC2: `list_document_notes` accepts optional `page` and `page_size` and forwards them | Parameters present in signature; forwarded to `notes.list()` | Parameters present and forwarded | ✅ Pass (unit) / ❌ Fail (integration — upstream bug) |
| 3 | AC3: Correctly unwraps `.results` and `.count` from `PagedResult` response | `ListResult(count=paged.count, items=paged.results)` | Correctly implemented | ✅ Pass (unit) / ❌ Fail (integration — upstream bug) |
| 4 | AC4: All unit tests for `list_document_notes` pass and cover updated return shape | All unit tests green | 229/229 unit tests pass | ✅ Pass |
| 5 | AC5: `ruff check` passes with no errors | No ruff violations | All checks passed | ✅ Pass |
| 6 | AC6: `mypy --strict` passes with no errors | No mypy errors | Success: no issues found in 12 source files | ✅ Pass |
| 7 | AC7: All existing unit and integration tests pass | Full suite green | 229 unit ✅, 22 other integration ✅, 5 document-notes integration ❌ | ❌ Fail |
| 8 | Edge: Issue 0015 marked as `RESOLVED` in index | Status = `RESOLVED` | Status = `RESOLVED` in `0000-general-index.md` | ✅ Pass |

### Bugs Found

#### BUG-001 — easypaperless 0.3.1 `notes.list()` crashes on real paperless-ngx instance [Severity: Critical]

**Steps to reproduce:**
1. Set up env vars with a live paperless-ngx instance.
2. Call `list_document_notes(document_id=<any valid id>)`.

**Expected:** Returns `PagedResult[DocumentNote]` as documented.
**Actual:** `AttributeError: 'list' object has no attribute 'get'` raised inside `easypaperless/_internal/http.py:309`.
**Root cause:** The paperless-ngx `/documents/{id}/notes/` endpoint returns a plain JSON array, not a paginated dict. easypaperless 0.3.1's `NotesResource.list()` calls `get_all_pages_paged()` which unconditionally calls `.get("count", 0)` on the response, expecting a `{"count": N, "results": [...]}` structure. The MCP implementation correctly follows the documented 0.3.1 API contract — the bug is entirely in the upstream library.
**Severity:** Critical — `list_document_notes` (and by extension `create`/`delete` in the round-trip test) is completely broken at runtime.
**Notes:** All other list tools are unaffected (their endpoints do return paginated responses). This needs to be fixed upstream in easypaperless. A new issue should be filed to track the upstream fix and a follow-up migration once it's released.
**Resolution:** Fixed in easypaperless 0.3.2. All 5 integration tests pass after upgrading.

### Automated Tests (0.3.1 — initial QA)
- Unit suite (`tests/unit/`): **229 passed, 0 failed** ✅
- Integration suite excl. document notes (`tests/integration/`): **22 passed, 0 failed** ✅
- Integration suite — document notes (`tests/integration/test_document_notes.py`): **0 passed, 5 failed** ❌
  - All 5 failures share the same root cause: BUG-001 (upstream easypaperless 0.3.1 defect)

### Summary (0.3.1 — initial QA)
- ACs tested: 7/7
- ACs passing: 6/7 (AC7 fails due to upstream bug, not MCP implementation)
- Bugs found: 1 (Critical: 1, High: 0, Medium: 0, Low: 0)
- Recommendation: ❌ Needs upstream fix before merge — `list_document_notes` is broken at runtime in all environments. The MCP implementation itself is correct; the blocker is easypaperless 0.3.1 shipping a `notes.list()` that is incompatible with the actual paperless-ngx API response format.

---

## Re-QA after easypaperless 0.3.2

**Tested by:** QA Engineer
**Date:** 2026-03-18
**easypaperless version:** 0.3.2
**Commit:** 06f5105

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | BUG-001 resolved: `list_document_notes` works on live instance | No crash, returns `ListResult[DocumentNote]` | 5/5 integration tests pass | ✅ Pass |
| 2 | AC1–AC3: Return shape, unwrapping, count | `ListResult` with `count` and `items` | Correct | ✅ Pass |
| 3 | AC4: Unit tests | 235 passed | 235 passed | ✅ Pass |
| 4 | AC5: `ruff check` | No errors | All checks passed | ✅ Pass |
| 5 | AC6: `mypy --strict` | No errors | Success: no issues found in 12 source files | ✅ Pass |
| 6 | AC7: Full suite | All tests green | 262 passed, 0 failed | ✅ Pass |

### Automated Tests (0.3.2 — re-QA)
- Unit suite (`tests/unit/`): **235 passed, 0 failed** ✅
- Integration suite (`tests/integration/`): **27 passed, 0 failed** ✅ (incl. all 5 document notes tests)

### Summary (0.3.2 — re-QA)
- ACs tested: 7/7
- ACs passing: 7/7
- Bugs found: 0
- Recommendation: ✅ Ready to merge — BUG-001 resolved by easypaperless 0.3.2. All ACs pass.
