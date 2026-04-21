# [FEATURE] Add `add_tags` / `remove_tags` parameters to `update_document`

## Summary

`update_document` currently accepts a `tags` parameter that **replaces** the entire tag list on the document. When an AI agent is asked to "add a tag", it often passes only the new tag, inadvertently wiping all existing tags. This feature adds `add_tags` and `remove_tags` convenience parameters that let agents safely modify individual tags without touching the rest.

---

## Problem Statement

The `tags` parameter in `update_document` is a full-replacement list. Nothing in the current docstring warns the agent about this destructive behavior. When an agent is instructed to "add tag X to document Y", it tends to call `update_document(id=Y, tags=[X])` — silently removing every pre-existing tag from the document.

---

## Proposed Solution

Extend `update_document` with two new optional parameters: `add_tags` and `remove_tags`. When either is provided, the tool:

1. Fetches the current document to obtain its existing tag list.
2. Applies the additions and/or removals to produce a new tag list.
3. Calls the underlying update API with the resulting full tag list.

Additionally, the docstring for the existing `tags` parameter must be updated to prominently warn that it **overwrites all existing tags**, and to recommend `add_tags` / `remove_tags` for incremental changes.

---

## User Stories

- As an AI agent, I want to add a tag to a document without knowing its current tags, so that I don't accidentally remove tags that were already assigned.
- As an AI agent, I want to remove a specific tag from a document without knowing its current tags, so that I can make targeted changes safely.

---

## Scope

### In Scope
- New `add_tags: list[int | str] | None` parameter on `update_document`.
- New `remove_tags: list[int | str] | None` parameter on `update_document`.
- When `add_tags` or `remove_tags` is provided: fetch current document tags, compute new list, pass full list to the API via the existing `tags` mechanism.
- Updated docstring on the `tags` parameter warning that it overwrites all existing tags, and pointing to `add_tags` / `remove_tags` for incremental changes.
- Unit tests covering: add only, remove only, add + remove combined, `tags` direct override still works.

### Out of Scope
- Changes to bulk tag tools (`bulk_add_tag`, `bulk_remove_tag`, `bulk_modify_tags`) — these already work correctly.
- Any changes to the easypaperless library itself.
- Adding `add_tags` / `remove_tags` to `upload_document`.

---

## Acceptance Criteria

- [ ] `update_document` accepts `add_tags: list[int | str] | None = None` and `remove_tags: list[int | str] | None = None`.
- [ ] When `add_tags` is provided, the tags in `add_tags` are merged with the document's current tags before the update is sent.
- [ ] When `remove_tags` is provided, the tags in `remove_tags` are removed from the document's current tags before the update is sent.
- [ ] `add_tags` and `remove_tags` can be used together in a single call.
- [ ] Using `add_tags` or `remove_tags` does not affect any other document field.
- [ ] The existing `tags` parameter still works as a full replacement when provided directly.
- [ ] If both `tags` and `add_tags`/`remove_tags` are provided, an error is raised (they are mutually exclusive).
- [ ] The `tags` parameter docstring explicitly states: *"Overwrites all existing tags. To add or remove individual tags without affecting others, use `add_tags` / `remove_tags` instead."*
- [ ] Unit tests pass for: add only, remove only, add + remove combined, direct `tags` override.
- [ ] Type checking (`mypy --strict`) passes.
- [ ] Linting (`ruff`) passes.

---

## Dependencies & Constraints

- Requires one extra `get_document` API call when `add_tags` or `remove_tags` is used (read-before-write).
- Tag identity comparison must handle both integer IDs and string names consistently (match by value against existing tag list).

---

## Priority
`Medium`

---

## Additional Notes

Existing `bulk_modify_tags` (documents.py line 531) implements the same pattern for multiple documents and can serve as a reference for the read-modify-write logic.

---

## QA

**Tested by:** QA Engineer  
**Date:** 2026-04-21  
**Commit:** 1cc43e3 (changes uncommitted in working tree)

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC: `add_tags` and `remove_tags` params exist with correct type `list[int \| str] \| None = None` | Params present with correct signatures | Present at documents.py:358-359 | ✅ Pass |
| 2 | AC: `add_tags` merges new tags with current document tags | Tags merged, API called with full list | `get` fetched then update called with merged list | ✅ Pass |
| 3 | AC: `remove_tags` removes tags from current document tags | Filtered tag list sent to API | Filtered correctly via set difference | ✅ Pass |
| 4 | AC: `add_tags` and `remove_tags` combined in single call | Both applied, one `get` call only | Applied together with one `get` | ✅ Pass |
| 5 | AC: `add_tags`/`remove_tags` do not affect other document fields | Only `tags` kwarg added to API call | Only `kwargs["tags"]` set; no other fields polluted | ✅ Pass |
| 6 | AC: Existing `tags` still works as full replacement | `get` not called; tags sent as-is | `get` not called; tags passed directly | ✅ Pass |
| 7 | AC: `tags` + `add_tags` raises `ValueError` (mutually exclusive) | `ValueError` with "mutually exclusive" message | Raised correctly | ✅ Pass |
| 8 | AC: `tags` + `remove_tags` raises `ValueError` (mutually exclusive) | `ValueError` with "mutually exclusive" message | Raised correctly | ✅ Pass |
| 9 | AC: `tags` docstring warns about overwrite + recommends `add_tags`/`remove_tags` | Warning text present | "WARNING: overwrites all existing tags…use add_tags / remove_tags instead" present | ✅ Pass |
| 10 | AC: Unit tests for add-only, remove-only, add+remove, direct tags override | All pass | 309/309 unit tests green | ✅ Pass |
| 11 | AC: `mypy --strict` passes | No type errors | "Success: no issues found in 14 source files" | ✅ Pass |
| 12 | AC: `ruff` passes | No lint errors | "All checks passed!" | ✅ Pass |
| 13 | Edge: `add_tags` deduplicates if tag already present | Tag added only once | Deduplication implemented; test coverage present | ✅ Pass |
| 14 | Edge: `remove_tags` with tag not in current list | Silently ignored, no error | Filtered via set — missing tag simply not in result | ✅ Pass |
| 15 | Edge: `remove_tags` string name vs integer ID in current list | String "5" does not match int 5 | Set comparison is value-based; mismatch expected, documented in docstring | ✅ Pass (documented limitation) |
| 16 | Edge: `add_tags=[]` (empty list, not None) | Triggers fetch + sends unchanged tags (minor extra call) | Empty list is not None, so fetch happens; tags unchanged | ✅ Pass (acceptable; no AC covers this) |

### Bugs Found

None.

### Automated Tests

- Suite: unit — 309 passed, 0 failed
- New tests added: `test_update_document_add_tags_merges_with_existing`, `test_update_document_add_tags_deduplicates`, `test_update_document_remove_tags_filters_existing`, `test_update_document_add_and_remove_tags_combined`, `test_update_document_add_remove_tags_fetches_document_once`, `test_update_document_tags_and_add_tags_raises`, `test_update_document_tags_and_remove_tags_raises`, `test_update_document_tags_direct_override_still_works`

### Summary

- ACs tested: 11/11
- ACs passing: 11/11
- Bugs found: 0
- Recommendation: ✅ Ready to merge

---

## Post-QA Fix — `remove_tags` string name resolution (2026-04-21)

**Issue identified during QA:** Row 15 above flagged that passing string names to `remove_tags` would silently fail to match because `current_doc.tags` returns integer IDs, making string-vs-int comparison always False. Although documented in the docstring, this behaviour was confusing and error-prone.

**Fix applied:**

- Added private helper `_resolve_tag_ids(client, tags)` in `documents.py`. Integers pass through unchanged; each string name is resolved to an integer ID via `client.tags.list(name_exact=name)`. Names that match no tag are silently ignored.
- Updated `remove_tags` path in `update_document` to call `_resolve_tag_ids` before filtering.
- Updated `remove_tags` docstring to remove the misleading caveat about string names not matching.
- Added 7 new unit tests: 5 covering `_resolve_tag_ids` directly, 2 covering the string-name removal flow in `update_document`.

**Results after fix:** 316/316 unit tests green, `mypy --strict` clean, `ruff` clean.
