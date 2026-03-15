# [FEATURE] Tags sub-server with full resource tool coverage

## Summary

Implement a dedicated MCP sub-server for the tags resource, exposing all methods and parameters from `easypaperless` `SyncTagsResource` as MCP tools. This enables AI agents to fully manage tags in paperless-ngx — listing, creating, updating, deleting, and bulk-operating on tags.

---

## Problem Statement

The tags resource is not yet exposed through the MCP server. AI agents cannot list existing tags, create new ones, update tag properties (including auto-matching rules, colour, inbox flag, hierarchy), or delete tags. This gap prevents AI agents from managing the tag taxonomy needed to classify and organise documents.

---

## Proposed Solution

Create `src/easypaperless_mcp/tools/tags.py` as a dedicated FastMCP sub-server, implementing all methods of `client.tags` (`SyncTagsResource`) as MCP tools. Mount the sub-server without namespace in `server.py`, following the same pattern used for the documents sub-server.

---

## User Stories

- As an AI agent, I want to list all tags (with optional name filters and pagination) so that I can discover which tags exist before classifying documents.
- As an AI agent, I want to get a single tag by ID so that I can inspect its properties.
- As an AI agent, I want to create a tag with a name, colour, inbox flag, and matching rules so that I can set up a new tag taxonomy.
- As an AI agent, I want to update an existing tag so that I can correct its name, colour, matching behaviour, or hierarchy.
- As an AI agent, I want to delete a single tag or bulk-delete multiple tags so that I can clean up unused tags.
- As an AI agent, I want to bulk-set permissions on multiple tags so that I can manage access control efficiently.

---

## Scope

### In Scope

- Create `src/easypaperless_mcp/tools/tags.py` with its own `FastMCP` sub-server instance
- Mount the tags sub-server without namespace in `server.py`
- Implement the following MCP tools with all parameters from the sync methods overview:
  - `list_tags` — parameters: `ids`, `name_contains`, `name_exact`, `page`, `page_size`, `ordering`, `descending`
  - `get_tag` — parameter: `id`
  - `create_tag` — parameters: `name`, `color`, `is_inbox_tag`, `match`, `matching_algorithm`, `is_insensitive`, `parent`, `owner`, `set_permissions`
  - `update_tag` — parameters: `id`, `name`, `color`, `is_inbox_tag`, `match`, `matching_algorithm`, `is_insensitive`, `parent`, `owner`, `set_permissions`
  - `delete_tag` — parameter: `id`
  - `bulk_delete_tags` — parameter: `ids`
  - `bulk_set_tag_permissions` — parameters: `ids`, `set_permissions`, `owner`, `merge`
- Return types: `list_tags` → `List[Tag]`; `get_tag`, `create_tag`, `update_tag` → `Tag`; delete/bulk tools → `None`
- Tool names follow verb-first, singular/plural cardinality convention from CLAUDE.md

### Out of Scope

- Changes to the documents sub-server or any other resource
- A `return_fields` parameter on tags tools (tags are small models; full return is acceptable)
- Changes to transport configuration

---

## Acceptance Criteria

- [ ] `tools/tags.py` exists and defines a `FastMCP` sub-server instance
- [ ] `server.py` mounts the tags sub-server without namespace alongside the existing documents sub-server
- [ ] `list_tags` is implemented with all 7 parameters (`ids`, `name_contains`, `name_exact`, `page`, `page_size`, `ordering`, `descending`) and returns `List[Tag]`
- [ ] `get_tag` is implemented with parameter `id` and returns `Tag`
- [ ] `create_tag` is implemented with all 9 parameters (`name`, `color`, `is_inbox_tag`, `match`, `matching_algorithm`, `is_insensitive`, `parent`, `owner`, `set_permissions`) and returns `Tag`
- [ ] `update_tag` is implemented with all 10 parameters (`id` + the same 9 as create) and returns `Tag`
- [ ] `delete_tag` is implemented with parameter `id` and returns `None`
- [ ] `bulk_delete_tags` is implemented with parameter `ids: List[int]` and returns `None`
- [ ] `bulk_set_tag_permissions` is implemented with parameters `ids`, `set_permissions`, `owner`, `merge` and returns `None`
- [ ] All 7 tools are registered and callable via the MCP server
- [ ] Tool names follow verb-first, singular/plural cardinality convention
- [ ] Return types use easypaperless Pydantic models directly (`Tag`)
- [ ] UNSET sentinel is used correctly for optional update parameters (distinguishes "not provided" from `None`)

---

## Dependencies & Constraints

- Depends on `easypaperless` package exposing all listed methods on `SyncPaperlessClient.tags`
- `MatchingAlgorithm` and `SetPermissions` types must be imported from `easypaperless` as needed
- UNSET sentinel must be used for `update_tag` parameters that support leave-unchanged semantics

---

## Priority

`High`

---

## Additional Notes

- easypaperless tags API reference: https://moritzgrenke.github.io/easypaperless/easypaperless/resources.html
- Pattern to follow: `tools/documents.py` and issue 0001
- `MatchingAlgorithm` enum values: `NONE | ANY_WORD | ALL_WORDS | EXACT | REGEX | FUZZY | AUTO`

---

## QA

**Tested by:** QA Engineer
**Date:** 2026-03-15
**Commit:** 6451f06

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC: `tools/tags.py` exists with FastMCP instance | File exists, `tags = FastMCP("tags")` defined | File exists, instance defined at line 8 | ✅ Pass |
| 2 | AC: `server.py` mounts tags sub-server without namespace | `mcp.mount(tags)` present | `mcp.mount(tags)` at line 10 | ✅ Pass |
| 3 | AC: `list_tags` has all 7 params and returns `List[Tag]` | All params present, `-> list[Tag]` | All 7 params (`ids`, `name_contains`, `name_exact`, `page`, `page_size`, `ordering`, `descending`), correct return type | ✅ Pass |
| 4 | AC: `get_tag` has `id` param and returns `Tag` | `id: int`, `-> Tag` | Correct | ✅ Pass |
| 5 | AC: `create_tag` has all 9 params and returns `Tag` | 9 params present | All 9 params present, correct return type | ✅ Pass |
| 6 | AC: `update_tag` has all 10 params and returns `Tag` | 10 params (`id` + 9 create params) | All 10 params present, correct return type | ✅ Pass |
| 7 | AC: `delete_tag` has `id` param and returns `None` | `id: int`, `-> None` | Correct | ✅ Pass |
| 8 | AC: `bulk_delete_tags` has `ids: List[int]` and returns `None` | `ids: list[int]`, `-> None` | Correct | ✅ Pass |
| 9 | AC: `bulk_set_tag_permissions` has 4 params and returns `None` | `ids`, `set_permissions`, `owner`, `merge` | All 4 params present, `-> None` | ✅ Pass |
| 10 | AC: All 7 tools registered and callable | 7 `@tags.tool` decorators | All 7 tools decorated | ✅ Pass |
| 11 | AC: Tool names follow verb-first convention | `list_tags`, `get_tag`, etc. | Correct naming throughout | ✅ Pass |
| 12 | AC: Return types use easypaperless Pydantic models directly | `Tag` used directly | `Tag` imported and used as return type | ✅ Pass |
| 13 | AC: UNSET sentinel used for optional update params | UNSET distinguishes "not provided" from `None` | `update_tag` uses `if param is not None` checks — `None` is silently skipped, making it impossible to clear nullable fields (`parent`, `owner`, `match`, `is_inbox_tag`) | ❌ Fail |
| 14 | Edge: `list_tags` with no args omits optional params from client call | No optional keys in kwargs | Confirmed: `ids`, `name_contains`, etc. omitted when None | ✅ Pass |
| 15 | Edge: `update_tag` with only `id` sends no kwargs | `kwargs == {}` | Correct, test confirms this | ✅ Pass |
| 16 | Edge: `update_tag` docstring claims `parent=None` clears parent | Documented behavior matches implementation | Docstring says "or None to clear" but `None` is skipped by `if parent is not None` guard | ❌ Fail |
| 17 | Regression: existing document tests still pass | 102 total unit tests pass | 102 passed | ✅ Pass |
| 18 | Static analysis: ruff lint | No issues | All checks passed | ✅ Pass |
| 19 | Static analysis: mypy (ignore-missing-imports) | No issues | Success: no issues found | ✅ Pass |

### Bugs Found

#### BUG-001 — `update_tag` cannot clear nullable fields; docstring is misleading [Severity: High]

**Steps to reproduce:**
1. Create a tag with a `parent` set (e.g., parent=5)
2. Call `update_tag(id, parent=None)` intending to remove the parent
3. Observe that the underlying `client.tags.update` is NOT called with `parent=None` — the value is silently skipped

**Expected:** Passing `None` for `parent`, `owner`, `match`, or `is_inbox_tag` sends `None` to the API (clearing the field), matching the docstring ("or None to clear").
**Actual:** The `if parent is not None` guard silently drops the value. The API receives no `parent` key at all (UNSET semantics = leave unchanged). There is no way to clear these nullable fields through the MCP tool.
**Severity:** High
**Notes:**
- The `client.tags.update` signature is `parent: str | None | _Unset = UNSET` — `UNSET` = leave alone, `None` = clear. The implementation conflates the two.
- `update_document` in `documents.py` solves this with `clear_*` boolean flags. `update_tag` needs equivalent `clear_parent`, `clear_owner`, `clear_match` flags **or** proper UNSET-based forwarding.
- The docstring for `update_tag.parent` explicitly states "or None to clear" — this is incorrect and will mislead AI agents.
- Affected nullable fields: `parent`, `owner`, `match`, `is_inbox_tag` (and arguably `matching_algorithm`).
- i don't want to use "clear_*" flags! implementation in update_document will be corrected. if param is left out (it should be UNSET by default) the field isn't updated. if explicitly pass None -> field is cleared.

### Automated Tests

- Suite: `tests/unit/test_tags.py` — 27 passed, 0 failed
- Suite: `tests/unit/` (all) — 102 passed, 0 failed
- Integration tests: Untested — requires live paperless-ngx instance

### Summary

- ACs tested: 13/13
- ACs passing: 11/13 (AC #13 fails; AC #16 is a documentation corollary of the same bug)
- Bugs found: 1 (Critical: 0, High: 1, Medium: 0, Low: 0)
- Recommendation: ❌ Needs fixes before merge — `update_tag` must be able to clear nullable fields (`parent`, `owner`, `match`) and the docstring must be corrected

---

## QA Round 2

**Tested by:** QA Engineer
**Date:** 2026-03-15
**Commit:** (uncommitted — post-fix state)

### Context

Re-QA after BUG-001 fix: `update_tag` was refactored to use `_UNSET` defaults and `is not UNSET` guards (same pattern as the corrected `update_document`). Issue 0006 (removing `clear_*` from `update_document`) was implemented in parallel.

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | BUG-001 fix: `update_tag` UNSET sentinel used correctly | All 9 optional params default to `_UNSET`; `if x is not UNSET` guards forward value (including `None`) | Confirmed — all params default to `_UNSET`, guards use `is not UNSET` | ✅ Pass |
| 2 | BUG-001 fix: `update_tag(id, parent=None)` sends `parent=None` to client | `kwargs["parent"] is None` | Confirmed by `test_update_tag_clears_nullable_fields_when_none_passed` | ✅ Pass |
| 3 | BUG-001 fix: docstring corrected — "Omit to leave unchanged, or None to clear" | Docstring accurately describes UNSET semantics | All nullable-field docstrings updated correctly | ✅ Pass |
| 4 | Regression: all 7 tools still present and correctly named | No regressions in tool set | All 7 `@tags.tool` decorators present | ✅ Pass |
| 5 | Regression: all unit tests pass | 102 passed, 0 failed | 102 passed, 0 failed | ✅ Pass |
| 6 | Static analysis: ruff lint on `tools/tags.py` | No issues | No issues in `tags.py` | ✅ Pass |
| 7 | Static analysis: mypy | No issues | Success: no issues found | ✅ Pass |

### Bugs Found

None.

### Automated Tests

- Suite: `tests/unit/test_tags.py` — 30 passed, 0 failed
- Suite: `tests/unit/` (all) — 102 passed, 0 failed
- Integration tests: Untested — requires live paperless-ngx instance

### Summary

- ACs tested: 13/13
- ACs passing: 13/13
- Bugs found: 0
- Recommendation: ✅ Ready to merge
