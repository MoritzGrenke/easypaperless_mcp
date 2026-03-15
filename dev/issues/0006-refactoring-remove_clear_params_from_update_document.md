# [REFACTORING] Remove `clear_*` params from `update_document`, use `None` to clear nullable fields

## Summary

The `update_document` tool currently uses a set of dedicated `clear_*: bool` parameters to clear nullable relational fields (e.g. `clear_correspondent`, `clear_document_type`). The underlying easypaperless library already uses `UNSET` as the default for these params and treats an explicit `None` as a clear signal. The tool should adopt this same convention: passing `None` for a nullable field clears it. The `clear_*` params must be removed.

---

## Current State

`update_document` exposes these extra boolean parameters:
- `clear_correspondent`
- `clear_document_type`
- `clear_storage_path`
- `clear_archive_serial_number`
- `clear_owner`

When set to `True`, the tool internally passes `None` to the corresponding easypaperless call. This duplicates the signalling mechanism already built into the easypaperless API and contradicts the project convention documented in CLAUDE.md ("If the api user wants to clear that field, he can achieve that by explicitly passing `None` to that param").

---

## Desired State

Each nullable field in `update_document` has a single parameter typed `int | None` (or the appropriate nullable type) with a default of `UNSET` (i.e. the field is omitted when not supplied). Passing `None` explicitly clears the field. No `clear_*` boolean parameters exist.

Docstrings clearly state that passing `None` removes/clears the field, and omitting the parameter leaves it unchanged.

---

## Motivation
- [x] Align with current standards / conventions
- [x] Reduce complexity
- [x] Improve readability

---

## Scope

### In Scope
- Remove all `clear_*` parameters from `update_document`
- Update the type signatures of the affected nullable parameters to accept `None`
- Update docstrings to document the `None`-clears pattern
- Update or remove any tests that relied on the `clear_*` parameters

### Out of Scope
- Other tools beyond `update_document`
- Changes to the easypaperless library itself
- Adding new update tools

---

## Risks & Considerations

- This is a breaking change to the `update_document` tool signature. Any existing AI usage relying on `clear_*` flags will need to switch to passing `None`.
- Tests that verify `clear_*` behavior must be updated to test the `None`-passing pattern instead.

---

## Acceptance Criteria
- [ ] `update_document` has no `clear_*` parameters.
- [ ] All formerly nullable fields (`correspondent`, `document_type`, `storage_path`, `archive_serial_number`, `owner`) accept `None` as an explicit value that clears the field.
- [ ] Omitting a nullable field leaves it unchanged (UNSET behavior preserved).
- [ ] Docstring for each nullable parameter states that passing `None` removes the value and omitting the parameter leaves it unchanged.
- [ ] All existing tests pass; tests that tested `clear_*` are updated to test the `None` pattern.

---

## Priority
`High`

---

## Additional Notes
- CLAUDE.md convention: "In easypaperless update methods have default UNSET for params related to fields that are nullable. If the api user wants to clear that field, he can achieve that by explicitly passing None to that param. use this method in update tools as well and make sure the docstring reflects it."
- Related tool: `src/easypaperless_mcp/tools/documents.py` — `update_document` function, lines ~325–410.

---

## QA

**Tested by:** QA Engineer
**Date:** 2026-03-15
**Commit:** (uncommitted — post-implementation state)

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC: no `clear_*` params in `update_document` | No `clear_correspondent`, `clear_document_type`, `clear_storage_path`, `clear_archive_serial_number`, `clear_owner` | Grep confirms zero `clear_` occurrences in `documents.py` | ✅ Pass |
| 2 | AC: `correspondent=None` clears the field | `kwargs["correspondent"] is None` forwarded to client | Confirmed by `test_update_document_none_clears_correspondent` | ✅ Pass |
| 3 | AC: `document_type=None` clears the field | `kwargs["document_type"] is None` forwarded to client | Confirmed by `test_update_document_none_clears_document_type` | ✅ Pass |
| 4 | AC: `storage_path=None` clears the field | `kwargs["storage_path"] is None` forwarded to client | Confirmed by `test_update_document_none_clears_storage_path` | ✅ Pass |
| 5 | AC: `archive_serial_number=None` clears the field | `kwargs["archive_serial_number"] is None` forwarded to client | Confirmed by `test_update_document_none_clears_archive_serial_number` | ✅ Pass |
| 6 | AC: `owner=None` clears the field | `kwargs["owner"] is None` forwarded to client | Confirmed by `test_update_document_none_clears_owner` | ✅ Pass |
| 7 | AC: omitting a nullable field leaves it unchanged (UNSET) | Field key absent from kwargs | Confirmed by `test_update_document_omits_correspondent_when_not_provided` and `test_update_document_no_kwargs_sent_for_none_fields` | ✅ Pass |
| 8 | AC: docstrings state "Omit to leave unchanged, or pass None to clear" | Each nullable param has correct docstring | Confirmed — all 5 nullable params have correct docstring language | ✅ Pass |
| 9 | AC: old `clear_*` tests removed/replaced with `None` pattern tests | No test references `clear_*` | Confirmed — `test_documents.py` uses `None`-passing pattern exclusively | ✅ Pass |
| 10 | Edge: `update_document(1)` sends no kwargs | `kwargs == {}` | Confirmed by `test_update_document_no_kwargs_sent_for_none_fields` | ✅ Pass |
| 11 | Static analysis: ruff lint | No issues | **E402** in `documents.py:12` — `from ..client import get_client` is placed after module-level `_UNSET: Any = UNSET` assignment | ❌ Fail |
| 12 | Static analysis: mypy | No issues | Success: no issues found | ✅ Pass |
| 13 | Regression: all unit tests pass | 102 passed, 0 failed | 102 passed, 0 failed | ✅ Pass |

### Bugs Found

#### BUG-001 — ruff E402 in `documents.py`: import after module-level assignment [Severity: Low]

**Steps to reproduce:**
1. Run `uv run ruff check .`
2. Observe: `E402 Module level import not at top of file` at `src/easypaperless_mcp/tools/documents.py:12`

**Expected:** All imports grouped at the top of the file before any module-level assignments.
**Actual:** `_UNSET: Any = UNSET` (line 10) is placed between the third-party imports and the relative import `from ..client import get_client` (line 12), triggering ruff E402.
**Severity:** Low
**Notes:** Moving `_UNSET: Any = UNSET` below the `from ..client import get_client` line (or using a `# noqa: E402` comment) would resolve this. `tags.py` avoids this issue by placing `_UNSET` after all imports.

### Automated Tests

- Suite: `tests/unit/` — 102 passed, 0 failed
- Integration tests: Untested — requires live paperless-ngx instance

### Summary

- ACs tested: 5/5
- ACs passing: 5/5
- Bugs found: 1 (Critical: 0, High: 0, Medium: 0, Low: 1)
- Recommendation: ❌ Needs fixes before merge — ruff lint violation must be resolved

---

## QA Round 2

**Tested by:** QA Engineer
**Date:** 2026-03-15
**Commit:** (uncommitted — post-bugfix state)

### Fix Applied

Moved `_UNSET: Any = UNSET` below all imports in `documents.py` (matching the arrangement in `tags.py`). BUG-001 resolved.

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | ruff lint | No issues | All checks passed | ✅ Pass |
| 2 | All unit tests pass | 102 passed, 0 failed | 102 passed, 0 failed | ✅ Pass |

### Summary

- Bugs found: 0
- Recommendation: ✅ Ready to merge
