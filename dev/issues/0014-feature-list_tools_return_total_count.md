# [FEATURE] Expose total count in list tool responses

## Summary
All `list_*` MCP tools (except `list_document_notes`) currently return only a plain list of items. Since easypaperless 0.3.0 the underlying `list()` methods return a paginated result object that also carries a `count` field — the total number of items matching the applied filters. This count should be surfaced to the AI so it can reason about pagination and the size of a result set without fetching all pages.

---

## Problem Statement
When an AI calls `list_documents` (or any other `list_*` tool) with filters, it receives only the current page of items. It has no way of knowing how many items match the filters in total, which makes efficient pagination and workload planning impossible.

---

## Proposed Solution
Each affected `list_*` tool should return a structured response that contains:
- `count` — the total number of items matching the filters (as provided by easypaperless)
- `items` — the list of resource objects (same as current return value)

The return type should be a small Pydantic model (or `TypedDict`) wrapping these two fields. The AI can then use `count` to decide whether to paginate, summarise scope, or report results to the user.

---

## User Stories

- As an AI agent, I want to know how many documents match my filters so that I can plan pagination and report accurate counts to the user.
- As an AI agent, I want to know how many tags/correspondents/document types/custom fields/storage paths exist so that I can decide whether to load all of them or work page by page.

---

## Scope

### In Scope
- `list_documents` in `tools/documents.py`
- `list_tags` in `tools/tags.py`
- `list_correspondents` in `tools/correspondents.py`
- `list_document_types` in `tools/document_types.py`
- `list_custom_fields` in `tools/custom_fields.py`
- `list_storage_paths` in `tools/storage_paths.py`
- Unit and integration tests updated to assert the new return structure

### Out of Scope
- `list_document_notes` — easypaperless still returns a plain list for notes; no change needed
- Adding next/previous pagination URLs or any other fields from the result object beyond `count`

---

## Acceptance Criteria
- [ ] Each affected `list_*` tool returns an object with a `count` field (int) and an `items` field (list of resource objects).
- [ ] `count` reflects the total number of matching items as returned by easypaperless, not just the number of items on the current page.
- [ ] `list_document_notes` is not changed and still returns `list[DocumentNote]`.
- [ ] All existing tests for the affected tools are updated to expect the new return structure and pass.
- [ ] `mypy --strict` reports no new errors.
- [ ] `ruff` reports no new lint errors.
- [ ] make sure the count return value is well documented - it is the total number of the documents in the paperless-ngx instance - not the returned number of items!

---

## Dependencies & Constraints
- Requires easypaperless >= 0.3.0 (already in use after issue 0013).
- The shape of the result object returned by easypaperless `list()` must expose a `count` attribute and an iterable of items; verify field names against the easypaperless 0.3.0 API reference before implementing.

---

## Priority
`Medium`

---

## Additional Notes
- easypaperless API reference: https://moritzgrenke.github.io/easypaperless/easypaperless/resources.html
- Related: issue 0013 (migration to easypaperless 0.3.0)

---

## QA

**Tested by:** QA Engineer
**Date:** 2026-03-17
**Commit:** (uncommitted changes on master)

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC1: All 6 affected `list_*` tools return `ListResult` with `count` + `items` | `ListResult[T]` returned | All 6 tools return `ListResult` via new `models.py` | ✅ Pass |
| 2 | AC2: `count` is total matching items (not page length) | `paged.count` from easypaperless | `paged.count` forwarded directly | ✅ Pass |
| 3 | AC3: `list_document_notes` unchanged, returns `list[DocumentNote]` | No change to signature | Signature still `list[DocumentNote]` at line 639 | ✅ Pass |
| 4 | AC4: All existing unit tests updated and passing | 228 unit tests pass | 228 passed, 0 failed | ✅ Pass |
| 4b | AC4: All existing integration tests updated and passing | Integration tests reflect new return structure | **Integration tests NOT updated** — 21 failed, 4 errors | ❌ Fail |
| 5 | AC5: `mypy --strict` no new errors | 0 errors | 0 errors in 12 source files | ✅ Pass |
| 6 | AC6: `ruff` no new lint errors | 0 warnings | All checks passed | ✅ Pass |
| 7 | AC7: `count` docstring describes total in paperless-ngx, not page count | Clear docstring distinction | `ListResult` class docstring and all 6 tool docstrings explicitly state "total number … in paperless-ngx — **not** just the number of items on the current page" | ✅ Pass |
| 8 | Edge: `ListResult` is generic (`ListResult[T]`) — mypy accepts all 6 concrete types | No mypy errors | Clean | ✅ Pass |
| 9 | Edge: Empty result set — `count=0, items=[]` | Works correctly | Unit tests cover empty case for all 6 tools | ✅ Pass |
| 10 | Regression: `list_document_notes` integration tests still pass | Notes tests unaffected | Notes tests erroring due to `list_documents` fixture returning `ListResult` (fixture calls `list_documents()` then does `docs[0]`) | ❌ Fail |

### Bugs Found

#### BUG-001 — Integration tests not updated to expect `ListResult` return structure [Severity: High]
**Steps to reproduce:**
1. Set `PAPERLESS_URL` and `PAPERLESS_TOKEN` env vars
2. Run `uv run pytest tests/integration/`

**Expected:** All integration tests pass with the new `ListResult` return structure.
**Actual:** 21 tests fail and 4 tests error. Failures are `AssertionError: assert False where False = isinstance(ListResult(...), list)` or `TypeError: 'ListResult' object is not subscriptable`.
**Affected files:**
- `tests/integration/test_tags.py` — 3 failures (asserts `isinstance(result, list)`, iterates `result` directly, indexes `result[0]`)
- `tests/integration/test_correspondents.py` — 3 failures (same pattern)
- `tests/integration/test_document_types.py` — 3 failures (same pattern)
- `tests/integration/test_storage_paths.py` — 5 failures + 1 error (same pattern; fixture `existing_storage_path_id` indexes `paths[0]`)
- `tests/integration/test_documents.py` — 3 failures (same pattern)
- `tests/integration/test_document_notes.py` — 3 errors (fixture `document_id` calls `list_documents()` and indexes `docs[0]` — cascades into notes tests)
**Severity:** High
**Notes:** Unit tests were correctly updated; only integration tests were missed. The AC explicitly states "Unit and integration tests updated to assert the new return structure."

### Automated Tests
- Unit suite: 228 passed, 0 failed ✅
- Integration suite: 21 failed, 4 errors ❌
  - `test_tags.py`: 3 failed
  - `test_correspondents.py`: 3 failed
  - `test_document_types.py`: 3 failed
  - `test_storage_paths.py`: 5 failed, 1 error
  - `test_documents.py`: 3 failed
  - `test_document_notes.py`: 3 errors (cascade from `list_documents` fixture)

### Summary
- ACs tested: 7/7
- ACs passing: 6/7 (AC4 partially fails — unit tests pass, integration tests do not)
- Bugs found: 1 (Critical: 0, High: 1, Medium: 0, Low: 0)
- Recommendation: ❌ Needs fixes before merge — integration tests must be updated to use `result.count` and `result.items` instead of treating the return value as a plain list.
