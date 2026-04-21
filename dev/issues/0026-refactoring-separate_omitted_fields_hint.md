# [REFACTORING] Separate `omitted_fields` hint into its own `omitted_fields_hint` field

## Summary

`omitted_fields` currently contains a mixed list: field names followed by a plain hint string appended as the last element. The hint string (`"Pass these field names in return_fields to include them."`) does not belong in a list of field names — it is a different type of data. The two concerns should be separated into distinct, typed fields.

---

## Current State

Both `list_documents` and `get_document` produce an `omitted_fields` value of type `list[str]` that looks like:

```
["added", "archive_serial_number", "content", ..., "Pass these field names in return_fields to include them."]
```

The hint string is appended as the final element of the same array that contains field names. A consumer (AI agent or human) cannot reliably distinguish field names from the hint without inspecting the string content. `ListResult.omitted_fields` is declared as `list[str]` but semantically holds two unrelated things.

---

## Desired State

`omitted_fields` contains only the names of the excluded fields — a clean `list[str]` with no trailing hint.

A new sibling field `omitted_fields_hint` (type `str`) carries the retrieval hint. It is populated whenever `omitted_fields` is non-empty, and absent (or an empty string) when all fields are included.

Example response shape after refactoring:

```
omitted_fields: ["added", "content", "page_count", ...]
omitted_fields_hint: "Pass these field names in return_fields to include them."
```

---

## Motivation

- [x] Improve readability
- [x] Align with current standards / conventions
- [x] Reduce complexity

---

## Scope

### In Scope
- `ListResult` model in `tools/models.py` — add `omitted_fields_hint: str = ""` field.
- `_compute_omitted_fields` helper in `tools/documents.py` — return only field names (no trailing hint string).
- `list_documents` — populate `omitted_fields_hint` on `ListResult` when fields are omitted.
- `get_document` — inject `omitted_fields_hint` into the result dict alongside `omitted_fields`.
- All unit tests that assert on the content of `omitted_fields` — update to reflect the new shape.

### Out of Scope
- Changing the hint text itself.
- Adding `return_fields` / `omitted_fields` support to tools that do not currently have it.
- Any other tools or response models.

---

## Risks & Considerations

- This is a **breaking change** to the response shape of `list_documents` and `get_document` — callers that read the last element of `omitted_fields` as the hint will break. Given that issue 0024 is freshly deployed in v0.3.0, the impact should be minimal.

---

## Acceptance Criteria

- [ ] `omitted_fields` in `ListResult` and in `get_document` responses contains only field name strings — no hint string appended.
- [ ] A new `omitted_fields_hint` field is present alongside `omitted_fields` whenever one or more fields are omitted, containing the retrieval hint.
- [ ] `omitted_fields_hint` is absent (or an empty string) when no fields are omitted.
- [ ] `_compute_omitted_fields` returns only field names — the hint is no longer part of its return value.
- [ ] All existing unit tests for `omitted_fields` are updated to match the new shape.
- [ ] `mypy --strict` passes.
- [ ] `ruff` passes.

---

## Priority
`Medium`

---

## Additional Notes

- Related to issue 0024 (`Make omitted return_fields transparent to AI agents`), which introduced the current mixed-list design.

---

## QA

**Tested by:** QA Engineer  
**Date:** 2026-04-21  
**Commit:** 1a45727

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC1: `omitted_fields` in `ListResult` contains only field name strings, no hint | Pure `list[str]` of field names | `omitted_fields: list[str] = []` in model; `_compute_omitted_fields` returns sorted field names only | ✅ Pass |
| 2 | AC1: `omitted_fields` in `get_document` response contains only field name strings | Pure `list[str]` of field names | `result["omitted_fields"] = omitted` where omitted is from `_compute_omitted_fields` | ✅ Pass |
| 3 | AC2: `omitted_fields_hint` present alongside `omitted_fields` when fields omitted | `omitted_fields_hint` non-empty string | `ListResult.omitted_fields_hint: str = ""`; populated with `_OMITTED_FIELDS_HINT` when omitted is non-empty | ✅ Pass |
| 4 | AC3: `omitted_fields_hint` is empty when no fields omitted | Empty string / absent | `list_documents` sets `omitted_fields_hint=""` when `omitted` is empty; `get_document` skips the block entirely | ✅ Pass |
| 5 | AC4: `_compute_omitted_fields` returns only field names, no hint | Return value is `list[str]` of field names | Returns `sorted(f for f in all_fields if f not in return_fields)` — hint absent | ✅ Pass |
| 6 | AC5: Unit tests for `omitted_fields` updated to new shape | Tests assert hint not in `omitted_fields`, hint in `omitted_fields_hint` | `test_compute_omitted_fields_returns_only_field_names`, `test_list_documents_omitted_fields_on_result`, `test_get_document_includes_omitted_fields_metadata` all verify new shape | ✅ Pass |
| 7 | AC6: `mypy --strict` passes | No type errors | `Success: no issues found in 14 source files` | ✅ Pass |
| 8 | AC7: `ruff` passes | No lint errors | `All checks passed!` | ✅ Pass |
| 9 | Edge: `list_documents` with empty result — `omitted_fields_hint` stays empty | `omitted_fields_hint == ""` | Tested by `test_list_documents_omitted_fields_empty_for_empty_results` — `omitted = []` branch returns `omitted_fields_hint=""` | ✅ Pass |
| 10 | Edge: `get_document` with all fields requested — `omitted_fields_hint` absent | Neither key present in response dict | `if omitted:` guard skips injection; tested by `test_get_document_no_omitted_fields_when_all_requested` | ✅ Pass |
| 11 | Regression: `_OMITTED_FIELDS_HINT` constant is not injected into `omitted_fields` list anywhere | Hint string never in `omitted_fields` | `_compute_omitted_fields` docstring explicitly documents this; `test_compute_omitted_fields_no_hint_in_list` verifies it | ✅ Pass |

### Bugs Found

None.

### Automated Tests

- Suite: unit — 327 passed, 0 failed

### Summary

- ACs tested: 7/7
- ACs passing: 7/7
- Bugs found: 0
- Recommendation: ✅ Ready to merge
