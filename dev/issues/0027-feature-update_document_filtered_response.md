# [FEATURE] Filtered response for `update_document` with `return_fields` support

## Summary

`update_document` currently returns the full `Document` model including large text fields like `content`. This is wasteful in an MCP context. The tool should behave like `get_document` and `list_documents`: return a compact default field set by default, support a `return_fields` parameter for customisation, and include `omitted_fields` / `omitted_fields_hint` metadata so AI agents know what was left out.

---

## Problem Statement

After a successful update, the AI agent receives the complete document — including `content`, which can be thousands of tokens long — even though it only cares about confirming that the update was applied. This wastes context and increases latency. There is no way to request a smaller response today.

---

## Proposed Solution

Add a `return_fields` parameter to `update_document` with a smart default that includes:
- `id` — always present for reference
- `modified` — confirms the update was accepted and shows the server-side timestamp
- every field that was explicitly passed as an argument to the call (the "updated fields")

When `return_fields` is omitted, the response contains only these fields. Fields not in `return_fields` are absent from the response entirely (not `null`). `omitted_fields` and `omitted_fields_hint` are added to the response following the same contract established by issue 0026:
- `omitted_fields` — list of field names that were excluded
- `omitted_fields_hint` — retrieval hint string, present only when fields were omitted

Passing an explicit `return_fields` list overrides the default entirely.

---

## User Stories

- As an AI agent, I want `update_document` to return only the fields I care about by default, so that I do not waste context on large text fields I did not request.
- As an AI agent, I want to see `modified` in every update response, so that I can confirm the update was accepted by the server.
- As an AI agent, I want to know which fields were omitted from the response, so that I can fetch them explicitly when needed.

---

## Scope

### In Scope
- New `return_fields: list[str] | None` parameter on `update_document`, defaulting to `None` (triggers smart default behaviour).
- Smart default: `id` + `modified` + every field whose argument was explicitly provided in the call.
- Response shape: filtered dict instead of raw `Document` model, with `omitted_fields` and `omitted_fields_hint` following the contract from issue 0026.
- Updated docstring for `update_document` describing the new parameter and default behaviour.
- Unit tests covering: default return fields, explicit `return_fields` override, `omitted_fields` / `omitted_fields_hint` presence and content.

### Out of Scope
- Changes to any other tool (`get_document`, `list_documents`, `upload_document`, bulk tools).
- Changing what fields the paperless-ngx API returns server-side.
- Implementation of issue 0026 itself — this issue depends on 0026 being completed first; the `omitted_fields` / `omitted_fields_hint` split must already be in place.

---

## Acceptance Criteria

- [ ] `update_document` accepts an optional `return_fields: list[str] | None` parameter.
- [ ] When `return_fields` is `None` (default), the response contains `id`, `modified`, and the fields that were explicitly passed as arguments to the call — nothing else.
- [ ] `id` is always present in the response regardless of `return_fields`.
- [ ] When `return_fields` is provided explicitly, the response contains exactly those fields (plus `id`).
- [ ] Fields not included in `return_fields` are absent from the response (not present as `null`).
- [ ] The response includes `omitted_fields` (list of excluded field names) and `omitted_fields_hint` (retrieval hint string) when one or more fields are omitted, following the contract defined in issue 0026.
- [ ] `omitted_fields` and `omitted_fields_hint` are absent (or empty) when all fields are included.
- [ ] The `update_document` docstring documents `return_fields` and describes the smart default behaviour.
- [ ] Unit tests pass for: smart default set, explicit override, omitted_fields metadata, all-fields case.
- [ ] `mypy --strict` passes.
- [ ] `ruff` passes.

---

## Dependencies & Constraints

- **Depends on issue 0026** — the `omitted_fields` / `omitted_fields_hint` separation must be implemented before this issue is implemented, so the correct response contract is available.
- The set of "fields explicitly passed by the caller" must be determined at runtime from the arguments received, not hardcoded.

---

## Priority
`Medium`

---

## Additional Notes

- Issue 0024 established the `return_fields` / `omitted_fields` pattern for `list_documents` and `get_document`. This issue extends the same pattern to `update_document`.
- Issue 0026 refactors the `omitted_fields` shape (separating the hint) — this issue builds on top of that refactored shape.

---

## QA

**Tested by:** QA Engineer  
**Date:** 2026-04-21  
**Commit:** 1a45727

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC1: `update_document` accepts `return_fields: list[str] \| None` | Parameter present with `None` default | `return_fields: list[str] \| None = None` at line 393 in `documents.py` | ✅ Pass |
| 2 | AC2: `return_fields=None` → smart default: `id` + `modified` + updated fields | Only those fields in response | Smart default logic builds `["id", "modified"]` then appends each updated field; tested by `test_update_document_default_always_includes_id_and_modified` and `test_update_document_default_includes_updated_field` | ✅ Pass |
| 3 | AC3: `id` always present regardless of `return_fields` | `id` in response | Smart default always starts with `"id"`; explicit override enforces it via `elif "id" not in return_fields: return_fields = ["id"] + return_fields`; tested by `test_update_document_id_always_present_in_explicit_return_fields` | ✅ Pass |
| 4 | AC4: Explicit `return_fields` overrides smart default entirely | Exactly those fields (+ `id`) returned | `return_fields` branch directly assigned; tested by `test_update_document_explicit_return_fields_overrides_default` | ✅ Pass |
| 5 | AC5: Fields not in `return_fields` absent (not null) | Keys missing from response dict | `_filter_fields` builds dict only for requested keys; tested by `test_update_document_default_excludes_non_updated_fields` | ✅ Pass |
| 6 | AC6: `omitted_fields` and `omitted_fields_hint` present when fields omitted | Both keys in response | `if omitted: result["omitted_fields"] = ...; result["omitted_fields_hint"] = ...`; tested by `test_update_document_omitted_fields_present_when_fields_omitted` | ✅ Pass |
| 7 | AC7: `omitted_fields` / `omitted_fields_hint` absent when all fields included | Neither key in response | `if omitted:` guard skips injection; tested by `test_update_document_omitted_fields_absent_when_all_fields_requested` | ✅ Pass |
| 8 | AC8: Docstring documents `return_fields` and smart default behaviour | Docstring present and accurate | Docstring at lines 439-442 describes default and override behaviour | ✅ Pass |
| 9 | AC9: Unit tests for smart default, explicit override, omitted metadata, all-fields | Tests exist and pass | `test_update_document_returns_dict`, `test_update_document_default_*`, `test_update_document_explicit_return_fields_overrides_default`, `test_update_document_omitted_fields_*` — all pass | ✅ Pass |
| 10 | AC10: `mypy --strict` passes | No type errors | `Success: no issues found in 14 source files` | ✅ Pass |
| 11 | AC11: `ruff` passes | No lint errors | `All checks passed!` | ✅ Pass |
| 12 | Edge: `tags`/`add_tags`/`remove_tags`/`remove_inbox_tags` each trigger `tags` in smart default | `tags` present in default response | Condition: `if tags is not None or add_tags is not None or remove_tags is not None or remove_inbox_tags is not None`; tested by `test_update_document_default_includes_tags_when_*` (3 tests) | ✅ Pass |
| 13 | Edge: `correspondent=None` (clear action) included in smart default | `correspondent` in response | `if correspondent is not UNSET:` is true for `None`; clearing correctly surfaces the cleared value | ✅ Pass |
| 14 | Edge: `set_permissions` not a readable document field — not in smart default | `set_permissions` absent (no matching document field) | `_filter_fields` silently skips unknown fields; correct behaviour since `set_permissions` is write-only | ✅ Pass |
| 15 | Regression: existing `update_document` tests unaffected | All prior tests pass | 327 unit tests pass; none broken by the new `return_fields` logic | ✅ Pass |

### Bugs Found

None.

### Automated Tests

- Suite: unit — 327 passed, 0 failed

### Summary

- ACs tested: 11/11
- ACs passing: 11/11
- Bugs found: 0
- Recommendation: ✅ Ready to merge
