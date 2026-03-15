# [FEATURE] Custom fields sub-server with full resource tool coverage

## Summary

Implement a dedicated MCP sub-server for the custom fields resource, exposing all methods and parameters from `easypaperless` `SyncCustomFieldsResource` as MCP tools. This enables AI agents to fully manage custom field definitions in paperless-ngx — listing, retrieving, creating, updating, and deleting custom fields.

---

## Problem Statement

The custom fields resource is not yet exposed through the MCP server. AI agents cannot list existing custom fields, create new ones, update their names or data types, or delete them. This gap prevents AI agents from managing the custom field schema needed to store structured metadata on documents.

---

## Proposed Solution

Create `src/easypaperless_mcp/tools/custom_fields.py` as a dedicated FastMCP sub-server, implementing all methods of `client.custom_fields` (`SyncCustomFieldsResource`) as MCP tools. Mount the sub-server without namespace in `server.py`, following the same pattern used for documents, tags, and correspondents sub-servers.

---

## User Stories

- As an AI agent, I want to list all custom fields (with optional name filters and pagination) so that I can discover which custom fields exist before working with document metadata.
- As an AI agent, I want to get a single custom field by ID so that I can inspect its properties and data type.
- As an AI agent, I want to create a custom field with a name and data type so that I can extend the metadata schema for documents.
- As an AI agent, I want to update an existing custom field so that I can correct its name, data type, or extra configuration.
- As an AI agent, I want to delete a custom field so that I can remove unused fields from the schema.

---

## Scope

### In Scope

- Create `src/easypaperless_mcp/tools/custom_fields.py` with its own `FastMCP` sub-server instance
- Mount the custom fields sub-server without namespace in `server.py`
- Implement the following MCP tools with all parameters from the sync methods overview:
  - `list_custom_fields` — parameters: `name_contains`, `name_exact`, `page`, `page_size`, `ordering`, `descending`
  - `get_custom_field` — parameter: `id`
  - `create_custom_field` — parameters: `name`, `data_type`, `extra_data`, `owner`, `set_permissions`
  - `update_custom_field` — parameters: `id`, `name`, `data_type`, `extra_data`
  - `delete_custom_field` — parameter: `id`
- Return types: `list_custom_fields` → `List[CustomField]`; `get_custom_field`, `create_custom_field`, `update_custom_field` → `CustomField`; `delete_custom_field` → `None`
- Tool names follow verb-first, singular/plural cardinality convention from CLAUDE.md
- UNSET sentinel used for all optional `update_custom_field` parameters; `None` clears the field, omitting leaves it unchanged

### Out of Scope

- Bulk delete or bulk set permissions — `SyncCustomFieldsResource` does not expose these methods
- Changes to documents, tags, correspondents, or any other existing sub-server
- Changes to transport configuration

---

## Acceptance Criteria

- [x] `tools/custom_fields.py` exists and defines a `FastMCP` sub-server instance
- [x] `server.py` mounts the custom fields sub-server without namespace alongside the existing sub-servers
- [x] `list_custom_fields` is implemented with all 6 parameters (`name_contains`, `name_exact`, `page`, `page_size`, `ordering`, `descending`) and returns `List[CustomField]`
- [x] `get_custom_field` is implemented with parameter `id` and returns `CustomField`
- [x] `create_custom_field` is implemented with all 5 parameters (`name`, `data_type`, `extra_data`, `owner`, `set_permissions`) and returns `CustomField`; `data_type` accepts the documented values: `string`, `boolean`, `integer`, `float`, `monetary`, `date`, `url`, `documentlink`, `select`
- [x] `update_custom_field` is implemented with all 4 parameters (`id`, `name`, `data_type`, `extra_data`) and returns `CustomField`; UNSET sentinel is used for all 3 optional params so that `None` clears and omitting leaves unchanged
- [x] `delete_custom_field` is implemented with parameter `id` and returns `None`
- [x] All 5 tools are registered and callable via the MCP server
- [x] Tool names follow verb-first, singular/plural cardinality convention
- [x] Return types use easypaperless Pydantic models directly (`CustomField`)
- [x] UNSET sentinel is used correctly for optional update parameters (distinguishes "not provided" from `None`)

---

## Dependencies & Constraints

- Depends on `easypaperless` package exposing all listed methods on `SyncPaperlessClient.custom_fields`
- `SetPermissions` type must be imported from `easypaperless` as needed for `create_custom_field`
- UNSET sentinel must be used for `update_custom_field` parameters that support leave-unchanged semantics
- `SyncCustomFieldsResource` has no `bulk_delete` or `bulk_set_permissions` — do not add these

---

## Priority

`High`

---

## Additional Notes

- easypaperless custom fields API reference: https://moritzgrenke.github.io/easypaperless/easypaperless/resources.html
- Pattern to follow: `tools/correspondents.py` and issue 0008
- `data_type` valid values: `string | boolean | integer | float | monetary | date | url | documentlink | select`
- Notable difference from other resources: `update_custom_field` does not support `owner` or `set_permissions` parameters — only `name`, `data_type`, and `extra_data` are updatable
- Notable difference from other resources: `list_custom_fields` has no `ids` filter parameter

---

## QA

**Tested by:** QA Engineer
**Date:** 2026-03-15
**Commit:** 9e2278a (HEAD — uncommitted implementation in working tree)

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC: `tools/custom_fields.py` exists with `FastMCP` instance | File exists, `custom_fields = FastMCP("custom_fields")` | File exists, instance named `custom_fields` | ✅ Pass |
| 2 | AC: `server.py` mounts custom_fields without namespace | `mcp.mount(custom_fields)` present | `mcp.mount(custom_fields)` present alongside documents, tags, correspondents | ✅ Pass |
| 3 | AC: `list_custom_fields` has all 6 params | `name_contains`, `name_exact`, `page`, `page_size`, `ordering`, `descending` | All 6 params present with correct types and defaults | ✅ Pass |
| 4 | AC: `list_custom_fields` returns `List[CustomField]` | Return type annotation and actual return | `list[CustomField]` annotation; integration test returns real objects | ✅ Pass |
| 5 | AC: `list_custom_fields` has no `ids` param | `ids` not in signature | Confirmed absent by unit test and code inspection | ✅ Pass |
| 6 | AC: `get_custom_field` takes `id`, returns `CustomField` | Calls `client.custom_fields.get(id=id)` | Calls correctly; integration round-trip passes | ✅ Pass |
| 7 | AC: `create_custom_field` has all 5 params | `name`, `data_type`, `extra_data`, `owner`, `set_permissions` | All 5 present; optional params omitted when None | ✅ Pass |
| 8 | AC: `create_custom_field` returns `CustomField` | Return type `CustomField` | Annotated and verified by unit test | ✅ Pass |
| 9 | AC: `update_custom_field` has all 4 params with UNSET defaults | `id`, `name`, `data_type`, `extra_data`; UNSET for optional 3 | All 4 present; `_UNSET` used as default; UNSET check gates forwarding | ✅ Pass |
| 10 | AC: `update_custom_field` None clears, omit leaves unchanged | UNSET ≠ None; both forwarded selectively | Unit tests confirm: omit → not in kwargs; None → forwarded as None | ✅ Pass |
| 11 | AC: `update_custom_field` has no `owner`/`set_permissions` | Params absent from signature | Confirmed absent; unit test verifies | ✅ Pass |
| 12 | AC: `delete_custom_field` takes `id`, returns `None` | Calls `client.custom_fields.delete(id=id)`, returns None | Correct call; return is None | ✅ Pass |
| 13 | AC: All 5 tools registered in server | MCP server lists all 5 tools | `mcp.mount(custom_fields)` registers all decorated tools | ✅ Pass |
| 14 | AC: Tool names follow verb-first convention | `list_`, `get_`, `create_`, `update_`, `delete_` prefix | All 5 tools comply | ✅ Pass |
| 15 | AC: Return types use Pydantic models directly | `CustomField` returned, not dict or primitive | All create/get/update/list tools return `CustomField` | ✅ Pass |
| 16 | Edge: `list_custom_fields` with all None params | No unexpected kwargs forwarded to client | Unit test confirms none of the optional kwargs present | ✅ Pass |
| 17 | Edge: `update_custom_field` called with only `id` | Empty kwargs dict forwarded | Unit test confirms `call_args.kwargs == {}` | ✅ Pass |
| 18 | Edge: `create_custom_field` minimal (name + data_type only) | Optional params not forwarded | Unit test confirms `extra_data`, `owner`, `set_permissions` absent | ✅ Pass |
| 19 | Lint: `ruff check` on `custom_fields.py` | No lint errors | All checks passed | ✅ Pass |
| 20 | Type check: `mypy` on `custom_fields.py` | No new mypy errors beyond pre-existing baseline | 1 pre-existing error (`easypaperless` missing stubs) — same as all other modules; no new errors | ✅ Pass |
| 21 | Integration: `list_custom_fields` against live instance | Returns a list | Returns `list` | ✅ Pass |
| 22 | Integration: list elements are `CustomField` objects | All elements are `CustomField` | Confirmed | ✅ Pass |
| 23 | Integration: `get_custom_field` round-trip | Fetched ID matches listed ID | Confirmed | ✅ Pass |

### Bugs Found

None.

### Automated Tests

- Unit suite: `tests/unit/test_custom_fields.py` — **23 passed**, 0 failed
- Integration suite: `tests/integration/test_custom_fields.py` — **3 passed**, 0 failed
- Lint: `ruff check` — clean
- Type check: `mypy` — 1 pre-existing error (missing `easypaperless` stubs), no new errors introduced

### Summary

- ACs tested: 11/11
- ACs passing: 11/11
- Bugs found: 0
- Recommendation: ✅ Ready to merge
