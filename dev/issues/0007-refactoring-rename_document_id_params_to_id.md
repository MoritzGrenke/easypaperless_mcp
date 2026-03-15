# [REFACTORING] Rename `document_id` / `document_ids` params to `id` / `ids` in documents tools

## Summary

All document resource tools currently use `document_id` (singular) and `document_ids` (plural) as parameter names. However, the paperless-ngx API and the easypaperless models always return the field as `id`. This mismatch causes AI agents to call tools with the wrong parameter name (e.g. `get_document(id=42)` instead of `get_document(document_id=42)`), resulting in tool call failures. Renaming the parameters to match the response field name eliminates the confusion.

---

## Current State

In `tools/documents.py`, the following tools have a `document_id` or `document_ids` parameter:

**Singular (`document_id: int`):**
- `get_document`
- `get_document_metadata`
- `update_document`
- `delete_document`
- `list_document_notes`
- `create_document_note`
- `delete_document_note` (also has `note_id`)

**Plural (`document_ids: list[int]`):**
- `bulk_add_tag`
- `bulk_remove_tag`
- `bulk_modify_tags`
- `bulk_delete_documents`
- `bulk_set_correspondent`
- `bulk_set_document_type`
- `bulk_set_storage_path`
- `bulk_modify_custom_fields`
- `bulk_set_permissions`

The response model (and all paperless-ngx API responses) uses `id` as the field name. When an AI agent reads a document response, it sees `id: 42`. When it then tries to call `get_document`, it naturally passes `id=42`, which fails because the parameter is named `document_id`.

---

## Desired State

All document tools in `tools/documents.py` use parameter names that match the response model field names:

- Singular document identity parameter: `id: int` (replaces `document_id`)
- Plural document identity parameter: `ids: list[int]` (replaces `document_ids`)
- The `note_id` parameter in `delete_document_note` is renamed to match the same convention — since it refers to a note's `id` field, it becomes `note_id` → unchanged is acceptable, but should be consistent with the notes resource convention if one is established.

Docstrings are updated to reflect the renamed parameters.

---

## Motivation
- [x] Align with current standards / conventions
- [x] Reduce complexity
- [x] Improve readability

---

## Scope

### In Scope
- Rename `document_id` → `id` in all singular document tools in `tools/documents.py`
- Rename `document_ids` → `ids` in all bulk document tools in `tools/documents.py`
- Update all docstrings referencing these parameters
- Update all tests that reference these parameter names

### Out of Scope
- Other sub-servers (tags, correspondents, etc.) — addressed separately if needed
- Changing any behavior or return values
- Renaming `note_id` in `delete_document_note` — it refers to a different resource and is not ambiguous

---

## Risks & Considerations

- Any existing MCP client configurations or saved conversations that call tools by positional argument will be unaffected. Calls using keyword arguments (`document_id=...`) will break after the rename — but this is intentional, as those calls are already broken from the AI's perspective (the AI passes `id=`, not `document_id=`).
- Tests in `tests/` that use keyword arguments must be updated.

---

## Acceptance Criteria
- [ ] Existing behavior is fully preserved (no functional changes).
- [ ] All singular document identity parameters are named `id` across all tools in `documents.py`.
- [ ] All plural document identity parameters are named `ids` across all bulk tools in `documents.py`.
- [ ] All docstrings in `documents.py` reference `id` / `ids` instead of `document_id` / `document_ids`.
- [ ] All tests that reference the old parameter names are updated.
- [ ] `mypy --strict` and `ruff` pass without new errors.

---

## Priority
`High`

---

## Additional Notes
- Observed in Claude Desktop: `get_document` was called with `id=...` (matching the response field name) instead of `document_id=...`, causing a tool call failure.
- Related to the general principle that AI agents infer parameter names from response payloads.

---

## QA

**Tested by:** QA Engineer
**Date:** 2026-03-15
**Commit:** 3744249 (working tree — not yet committed)

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC1: Behavior preserved — all 7 singular tools pass their `id` arg correctly to the easypaperless client | Client called with unchanged positional/keyword args | 102 unit tests pass, verified via runtime introspection | ✅ Pass |
| 2 | AC2: All singular tools use `id` as first param | `id: int` for `get_document`, `get_document_metadata`, `update_document`, `delete_document`, `list_document_notes`, `create_document_note`, `delete_document_note` | All 7 confirmed via `inspect.signature` at runtime | ✅ Pass |
| 3 | AC3: All bulk tools use `ids` as first param | `ids: list[int]` for all 9 bulk tools | All 9 confirmed via `inspect.signature` at runtime | ✅ Pass |
| 4 | AC4: Docstrings reference `id`/`ids` — no stale `document_id`/`document_ids` | Zero matches for `document_id` or `document_ids` in `documents.py` | `grep` found no matches | ✅ Pass |
| 5 | AC5: Tests updated — no stale parameter names | Zero matches for `document_id`/`document_ids` in `tests/` | `grep` found no matches | ✅ Pass |
| 6 | AC6: `ruff` passes without new errors | No new ruff violations | `ruff check src/ tests/` → all checks passed | ✅ Pass |
| 7 | AC6: `mypy --strict` — no new errors introduced | Error count unchanged from baseline | 8 errors before and after (all pre-existing: missing stubs, `PydanticUndefined`, `no-any-return` in tags.py) | ✅ Pass |
| 8 | Edge: `note_id` param in `delete_document_note` unchanged | `note_id` stays as-is (explicitly out of scope) | `note_id` confirmed unchanged | ✅ Pass |
| 9 | Edge: `list_documents` `ids` filter param unchanged | `ids` was already correct in `list_documents` (not a document identity param) | Unchanged, no regression | ✅ Pass |
| 10 | Regression: tags sub-server unaffected | No changes to `tags.py` or tag tests | 28 tag unit tests pass unchanged | ✅ Pass |

### Bugs Found

None.

### Automated Tests
- Suite: `tests/unit/` — 102 passed, 0 failed
- Suite: `tests/integration/` — Untested (requires live paperless-ngx instance with `PAPERLESS_URL` and `PAPERLESS_TOKEN`)

### Summary
- ACs tested: 6/6
- ACs passing: 6/6
- Bugs found: 0
- Recommendation: ✅ Ready to merge
