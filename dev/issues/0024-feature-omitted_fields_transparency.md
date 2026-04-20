# [FEATURE] Make omitted `return_fields` transparent to AI agents

## Summary

When a tool uses `return_fields` to filter its response, excluded fields are currently replaced with `None` / zero values instead of being absent from the response. AI agents interpret these `None` values as real data (e.g. "this document has no content"), leading to incorrect conclusions and unnecessary follow-up calls. This feature makes omitted fields transparent so that any AI agent naturally understands what is available but not shown.

---

## Problem Statement

Tools such as `list_documents` and `get_document` accept a `return_fields` parameter. When fields are not included, `_filter_fields` sets them to `None` (or type-appropriate zero values like `""`, `0`, `[]`) before returning the model. The serialized response therefore contains `"content": null`, `"content_word_count": 0`, etc.

An AI agent receiving this response has no signal that these values were intentionally omitted. It reads `null` as the authoritative value and reports back, for example, that a document has no content. This causes incorrect answers and erodes user trust.

The problem currently exists in the documents tools (`list_documents`, `get_document`) and applies to any future tool that uses the same `_filter_fields` pattern.

---

## Proposed Solution

Two complementary changes are required:

1. **Remove omitted fields entirely** instead of replacing them with `None` / zero values. The serialized response should only contain the keys that are actually populated. An absent key carries no meaning; a `null` key does.

2. **Inject an `_omitted_fields` metadata entry** into every filtered response listing the field names that were excluded and a hint that they can be retrieved by adding them to `return_fields`. This gives the AI agent an explicit, machine-readable signal about what is missing and how to get it.

Both changes must be applied consistently to every tool that uses a `return_fields` filter.

---

## User Stories

- As an AI agent, I want the response to only include fields that were actually returned, so that I do not misinterpret absent data as real values.
- As an AI agent, I want the response to tell me which fields were omitted and how to include them, so that I can fetch them when needed without guessing parameter names.
- As a user, I want Claude to stop reporting that documents have no content when they simply were not fetched, so that I can trust the answers I receive.

---

## Scope

### In Scope
- Modify `_filter_fields` (or its equivalent) so that omitted fields are excluded from serialization rather than set to `None` / zero.
- Add an `_omitted_fields` field (type `list[str]`) to every response wrapper or model that uses `return_fields` filtering, populated with the names of all excluded fields plus a hint string (e.g. `"Pass these field names in return_fields to include them."`).
- Apply both changes to all tools in `documents.py` that use `return_fields` today (`list_documents`, `get_document`).
- Apply both changes to any other tool that adopts the same pattern in the future (ensure the helper is shared and re-usable).

### Out of Scope
- Changing the default value of `return_fields` for any tool.
- Adding `return_fields` support to tools that do not currently have it.
- Modifying the easypaperless library itself.

---

## Acceptance Criteria
- [ ] When `list_documents` is called with the default `return_fields`, the serialized response objects do **not** contain keys for omitted fields (e.g. `content`, `content_word_count` are absent, not `null`).
- [ ] Every response item (or the containing list result) includes an `_omitted_fields` entry listing all field names that were excluded and a short hint on how to retrieve them via `return_fields`.
- [ ] When `return_fields=None` (all fields requested), `_omitted_fields` is absent or an empty list — no false positives.
- [ ] The same behavior applies to `get_document` and any other tool using the shared `_filter_fields` helper.
- [ ] Existing unit tests for `_filter_fields` are updated to reflect the new behavior; new tests cover the `_omitted_fields` metadata.
- [ ] No regression in tools that do not use `return_fields` filtering.

---

## Dependencies & Constraints

- The `_filter_fields` helper currently returns a Pydantic `Document` model copy. To exclude keys from serialization, the approach must ensure `model_serializer` / `model_dump(exclude_unset=True)` or an equivalent mechanism is used without breaking FastMCP's serialization pipeline.
- The `_omitted_fields` field must either be added to the `Document` model or carried in the `ListResult` wrapper — whichever avoids polluting the upstream easypaperless model.

---

## Priority
`High`

---

## Additional Notes

- Issue 0003 and 0017 addressed crashes caused by `_filter_fields` setting required fields to `None`. This issue addresses the semantic problem: even when the filtering is crash-free, `None` values mislead AI agents.
- The `_omitted_fields` hint text should name the correct parameter (`return_fields`) so an AI agent can construct the corrected call without additional lookups.

---

## QA

**Tested by:** QA Engineer  
**Date:** 2026-04-21  
**Commit:** f5a7b09 (working tree changes, unstaged)

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC1: `list_documents` default `return_fields` — omitted fields are absent from items (not `null`) | Keys like `content`, `page_count` absent from item dicts | `_filter_fields` returns a plain dict with only requested keys; confirmed by `test_list_documents_return_fields_id_title_only` | ✅ Pass |
| 2 | AC2: Every `list_documents` response includes `omitted_fields` listing excluded names + hint | `result.omitted_fields` is non-empty list with field names and hint string | `ListResult.omitted_fields` populated from `_compute_omitted_fields`; `test_list_documents_omitted_fields_on_result` confirms content + hint | ✅ Pass |
| 3 | AC2: `get_document` result includes `omitted_fields` key | `result["omitted_fields"]` present with excluded names + hint | `get_document` injects key when `omitted` is non-empty; `test_get_document_includes_omitted_fields_metadata` confirms | ✅ Pass |
| 4 | AC3: When all model fields are explicitly requested, `omitted_fields` is absent or empty | Empty `omitted_fields` on `ListResult`; no `omitted_fields` key in `get_document` dict | `test_list_documents_omitted_fields_empty_when_all_fields_included` + `test_get_document_no_omitted_fields_when_all_requested` pass | ✅ Pass |
| 5 | AC3 (ambiguity): `return_fields=None` yields non-empty `omitted_fields` | AC3 parenthetically claims `None` = "all fields"; but implementation treats `None` as "use default subset" — so `omitted_fields` is NOT empty | `test_list_documents_default_return_fields_preserves_list_fields` confirms `None` → `_LIST_RETURN_FIELDS`, not all fields. AC3 wording is misleading but implementation intent is correct. | ⚠️ Ambiguous |
| 6 | AC4: `get_document` uses the same shared helpers | Both tools call `_filter_fields` and `_compute_omitted_fields` | Confirmed in code; `test_get_document_returns_filtered` + omitted_fields tests pass | ✅ Pass |
| 7 | AC5: Existing `_filter_fields` tests updated to reflect dict return type | Old tests pass with new dict-returning `_filter_fields` | All 5 `test_filter_fields_*` tests pass; `test_filter_fields_returns_only_requested_keys` explicitly checks for absent keys | ✅ Pass |
| 8 | AC5: New tests cover `_compute_omitted_fields` and `omitted_fields` metadata | Tests exist for compute function + list + get omitted_fields behavior | 3 `test_compute_omitted_fields_*` + 3 `test_list_documents_omitted_fields_*` + 2 `test_get_document_*_omitted` tests present | ✅ Pass |
| 9 | AC6: No regression in tools without `return_fields` | All non-documents tests still pass | All 301 unit tests pass | ✅ Pass |
| 10 | Edge: `list_documents` with empty results — `omitted_fields` is empty | `result.omitted_fields == []` | `omitted = _compute_omitted_fields(docs[0], return_fields) if docs else []` — guarded; `test_list_documents_omitted_fields_empty_for_empty_results` passes | ✅ Pass |
| 11 | Edge: `id` always injected even when missing from `return_fields` | `id` present in all item dicts | `if "id" not in return_fields: return_fields = ["id"] + return_fields`; regression tests pass | ✅ Pass |
| 12 | Edge: Unknown field name in `return_fields` silently skipped | No crash, unknown field absent from result | `_filter_fields` uses `if f in all_fields` guard; `test_filter_fields_unknown_field_silently_skipped` passes | ✅ Pass |

### Bugs Found

#### BUG-001 — AC3 wording incorrectly equates `return_fields=None` with "all fields requested" [Severity: Low]

**Steps to reproduce:**
1. Read AC3: "When `return_fields=None` (all fields requested), `_omitted_fields` is absent or an empty list"
2. Call `list_documents(return_fields=None)` — maps to `_LIST_RETURN_FIELDS` (a curated subset), not all model fields
3. Observe that `omitted_fields` is non-empty (contains `content`, `page_count`, etc.)

**Expected (per AC3 as written):** `omitted_fields` should be empty  
**Actual:** `omitted_fields` is non-empty — lists fields absent from `_LIST_RETURN_FIELDS`  
**Severity:** Low — implementation intent is correct (empty only when *all* fields explicitly passed); the AC wording is misleading, not the code  
**Notes:** The unit tests correctly use `return_fields=all_fields` (not `None`) to test the "all fields" path. The AC3 parenthetical `(all fields requested)` is inaccurate. This is a documentation issue only — no code change needed, but AC3 should be reworded in the issue to avoid confusion.

### Automated Tests
- Suite: `tests/unit` — 301 passed, 0 failed
- mypy: no issues found in 14 source files
- ruff: all checks passed

### Summary
- ACs tested: 6/6
- ACs passing: 5/6 (AC3 passes in spirit but has misleading wording — see BUG-001)
- Bugs found: 1 (Critical: 0, High: 0, Medium: 0, Low: 1)
- Recommendation: ✅ Ready to merge — BUG-001 is a documentation ambiguity only, implementation behavior is correct
