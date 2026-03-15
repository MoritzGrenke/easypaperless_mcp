# [FEATURE] Correspondents sub-server with full resource tool coverage

## Summary

Implement a dedicated MCP sub-server for the correspondents resource, exposing all methods and parameters from `easypaperless` `SyncCorrespondentsResource` as MCP tools. This enables AI agents to fully manage correspondents in paperless-ngx — listing, creating, updating, deleting, and bulk-operating on correspondents.

---

## Problem Statement

The correspondents resource is not yet exposed through the MCP server. AI agents cannot list existing correspondents, create new ones, update correspondent properties (including auto-matching rules), or delete correspondents. This gap prevents AI agents from managing the correspondent taxonomy needed to classify and organise documents.

---

## Proposed Solution

Create `src/easypaperless_mcp/tools/correspondents.py` as a dedicated FastMCP sub-server, implementing all methods of `client.correspondents` (`SyncCorrespondentsResource`) as MCP tools. Mount the sub-server without namespace in `server.py`, following the same pattern used for the documents and tags sub-servers.

---

## User Stories

- As an AI agent, I want to list all correspondents (with optional name filters and pagination) so that I can discover which correspondents exist before classifying documents.
- As an AI agent, I want to get a single correspondent by ID so that I can inspect its properties.
- As an AI agent, I want to create a correspondent with a name and matching rules so that I can set up a new correspondent taxonomy.
- As an AI agent, I want to update an existing correspondent so that I can correct its name or matching behaviour.
- As an AI agent, I want to delete a single correspondent or bulk-delete multiple correspondents so that I can clean up unused correspondents.
- As an AI agent, I want to bulk-set permissions on multiple correspondents so that I can manage access control efficiently.

---

## Scope

### In Scope

- Create `src/easypaperless_mcp/tools/correspondents.py` with its own `FastMCP` sub-server instance
- Mount the correspondents sub-server without namespace in `server.py`
- Implement the following MCP tools with all parameters from the sync methods overview:
  - `list_correspondents` — parameters: `ids`, `name_contains`, `name_exact`, `page`, `page_size`, `ordering`, `descending`
  - `get_correspondent` — parameter: `id`
  - `create_correspondent` — parameters: `name`, `match`, `matching_algorithm`, `is_insensitive`, `owner`, `set_permissions`
  - `update_correspondent` — parameters: `id`, `name`, `match`, `matching_algorithm`, `is_insensitive`, `owner`, `set_permissions`
  - `delete_correspondent` — parameter: `id`
  - `bulk_delete_correspondents` — parameter: `ids`
  - `bulk_set_correspondent_permissions` — parameters: `ids`, `set_permissions`, `owner`, `merge`
- Return types: `list_correspondents` → `List[Correspondent]`; `get_correspondent`, `create_correspondent`, `update_correspondent` → `Correspondent`; delete/bulk tools → `None`
- Tool names follow verb-first, singular/plural cardinality convention from CLAUDE.md
- UNSET sentinel used for all optional `update_correspondent` parameters; `None` clears the field, omitting leaves it unchanged

### Out of Scope

- Changes to the documents or tags sub-server or any other resource
- Changes to transport configuration

---

## Acceptance Criteria

- [ ] `tools/correspondents.py` exists and defines a `FastMCP` sub-server instance
- [ ] `server.py` mounts the correspondents sub-server without namespace alongside the existing sub-servers
- [ ] `list_correspondents` is implemented with all 7 parameters (`ids`, `name_contains`, `name_exact`, `page`, `page_size`, `ordering`, `descending`) and returns `List[Correspondent]`
- [ ] `get_correspondent` is implemented with parameter `id` and returns `Correspondent`
- [ ] `create_correspondent` is implemented with all 6 parameters (`name`, `match`, `matching_algorithm`, `is_insensitive`, `owner`, `set_permissions`) and returns `Correspondent`
- [ ] `update_correspondent` is implemented with all 7 parameters (`id` + the same 6 as create) and returns `Correspondent`; UNSET sentinel is used for all optional params so that `None` clears and omitting leaves unchanged
- [ ] `delete_correspondent` is implemented with parameter `id` and returns `None`
- [ ] `bulk_delete_correspondents` is implemented with parameter `ids: List[int]` and returns `None`
- [ ] `bulk_set_correspondent_permissions` is implemented with parameters `ids`, `set_permissions`, `owner`, `merge` and returns `None`
- [ ] All 7 tools are registered and callable via the MCP server
- [ ] Tool names follow verb-first, singular/plural cardinality convention
- [ ] Return types use easypaperless Pydantic models directly (`Correspondent`)
- [ ] UNSET sentinel is used correctly for optional update parameters (distinguishes "not provided" from `None`)

---

## Dependencies & Constraints

- Depends on `easypaperless` package exposing all listed methods on `SyncPaperlessClient.correspondents`
- `MatchingAlgorithm` and `SetPermissions` types must be imported from `easypaperless` as needed
- UNSET sentinel must be used for `update_correspondent` parameters that support leave-unchanged semantics

---

## Priority

`High`

---

## Additional Notes

- easypaperless correspondents API reference: https://moritzgrenke.github.io/easypaperless/easypaperless/resources.html
- Pattern to follow: `tools/tags.py` and issue 0005
- `MatchingAlgorithm` enum values: `NONE | ANY_WORD | ALL_WORDS | EXACT | REGEX | FUZZY | AUTO`

---

## QA

**Tested by:** QA Engineer
**Date:** 2026-03-15
**Commit:** unstaged (feature/0008-correspondents-subserver)

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC: `tools/correspondents.py` exists and defines a `FastMCP` instance | File present, `correspondents = FastMCP("correspondents")` | File present at `src/easypaperless_mcp/tools/correspondents.py`, instance defined | ✅ Pass |
| 2 | AC: `server.py` mounts correspondents without namespace | `mcp.mount(correspondents)` present | `mcp.mount(correspondents)` added, no namespace arg | ✅ Pass |
| 3 | AC: `list_correspondents` has all 7 params and returns `List[Correspondent]` | `ids`, `name_contains`, `name_exact`, `page`, `page_size`, `ordering`, `descending` present; return `list[Correspondent]` | All 7 params present; return type annotated `list[Correspondent]`; unit tests pass all param paths | ✅ Pass |
| 4 | AC: `get_correspondent` takes `id`, returns `Correspondent` | `get_correspondent(id: int) -> Correspondent` | Implemented; `client.correspondents.get(id=id)` called; unit test passes | ✅ Pass |
| 5 | AC: `create_correspondent` has all 6 params, returns `Correspondent` | `name`, `match`, `matching_algorithm`, `is_insensitive`, `owner`, `set_permissions` | All 6 params present; `is_insensitive=True` default; `None` optionals omitted from client call | ✅ Pass |
| 6 | AC: `update_correspondent` has 7 params, UNSET for optional, `None` clears | UNSET sentinel on all optional params; `None` forwarded, UNSET omitted | `_UNSET` applied to all 6 optional params; UNSET check gates each kwarg; unit test for clearing confirms `None` forwarded | ✅ Pass |
| 7 | AC: `delete_correspondent` takes `id`, returns `None` | `delete_correspondent(id: int) -> None` | Implemented; `client.correspondents.delete(id=id)` called; returns `None` | ✅ Pass |
| 8 | AC: `bulk_delete_correspondents` takes `ids: List[int]`, returns `None` | Calls `client.correspondents.bulk_delete(ids)` | Implemented correctly; unit test passes | ✅ Pass |
| 9 | AC: `bulk_set_correspondent_permissions` has `ids`, `set_permissions`, `owner`, `merge` | All 4 params, delegates to `bulk_set_permissions` | Implemented; defaults `set_permissions=None`, `owner=None`, `merge=False`; unit tests for all cases pass | ✅ Pass |
| 10 | AC: All 7 tools registered and callable | All decorated with `@correspondents.tool` | Confirmed in source; all 7 decorators present | ✅ Pass |
| 11 | AC: Tool names follow verb-first, singular/plural convention | `list_correspondents`, `get_correspondent`, etc. | All 7 names conform to convention | ✅ Pass |
| 12 | AC: Return types use easypaperless Pydantic models directly | `Correspondent` used in annotations | `from easypaperless import Correspondent` used throughout | ✅ Pass |
| 13 | AC: UNSET sentinel distinguishes "not provided" from `None` | Omitted params not forwarded; `None` forwarded | `if x is not UNSET: kwargs[...] = x` pattern; unit test `test_update_correspondent_no_extra_kwargs_when_only_id` confirms | ✅ Pass |
| 14 | Edge: `list_correspondents` with no args omits all optional params | `descending=False` always sent; other optionals absent | Confirmed by `test_list_correspondents_omits_none_optional_params` | ✅ Pass |
| 15 | Edge: `create_correspondent` with only `name` omits optional params | No `match`, `matching_algorithm`, etc. in client call | Confirmed by `test_create_correspondent_omits_none_optional_params` | ✅ Pass |
| 16 | Edge: `update_correspondent` with only `id` sends empty kwargs | `client.correspondents.update(id, **{})` | Confirmed by `test_update_correspondent_no_extra_kwargs_when_only_id` | ✅ Pass |
| 17 | Regression: existing unit tests unaffected | All prior 102 unit tests still pass | 130 total unit tests pass (28 new + 102 existing) | ✅ Pass |
| 18 | Static analysis: ruff check | No linting errors | `All checks passed!` | ✅ Pass |
| 19 | Static analysis: mypy | No new type errors | Pre-existing `import-untyped` error for `easypaperless` (affects all modules equally, not introduced by this issue) | ✅ Pass (pre-existing) |
| 20 | Integration: `list_correspondents` and `get_correspondent` round-trip | Returns valid `Correspondent` objects | All 3 integration tests pass against live instance | ✅ Pass |

### Bugs Found

No bugs found.

### Automated Tests

- Suite: `tests/unit/test_correspondents.py` — 28 passed, 0 failed
- Suite: `tests/unit/` (full) — 130 passed, 0 failed
- Suite: `tests/integration/test_correspondents.py` — 3 passed, 0 failed

### Summary

- ACs tested: 13/13
- ACs passing: 13/13
- Bugs found: 0
- Recommendation: ✅ Ready to merge
