# [FEATURE] Document types sub-server with full resource tool coverage

## Summary

Implement a dedicated MCP sub-server for the document types resource, exposing all methods and parameters from `easypaperless` `SyncDocumentTypesResource` as MCP tools. This enables AI agents to fully manage document types in paperless-ngx — listing, creating, updating, deleting, and bulk-operating on document types.

---

## Problem Statement

The document types resource is not yet exposed through the MCP server. AI agents cannot list existing document types, create new ones, update their properties (including auto-matching rules), or delete them. This gap prevents AI agents from managing the document type taxonomy needed to classify and organise documents.

---

## Proposed Solution

Create `src/easypaperless_mcp/tools/document_types.py` as a dedicated FastMCP sub-server, implementing all methods of `client.document_types` (`SyncDocumentTypesResource`) as MCP tools. Mount the sub-server without namespace in `server.py`, following the same pattern used for the tags and correspondents sub-servers.

---

## User Stories

- As an AI agent, I want to list all document types (with optional name filters and pagination) so that I can discover which document types exist before classifying documents.
- As an AI agent, I want to get a single document type by ID so that I can inspect its properties.
- As an AI agent, I want to create a document type with a name and matching rules so that I can set up a new document type taxonomy.
- As an AI agent, I want to update an existing document type so that I can correct its name or matching behaviour.
- As an AI agent, I want to delete a single document type or bulk-delete multiple document types so that I can clean up unused types.
- As an AI agent, I want to bulk-set permissions on multiple document types so that I can manage access control efficiently.

---

## Scope

### In Scope

- Create `src/easypaperless_mcp/tools/document_types.py` with its own `FastMCP` sub-server instance
- Mount the document types sub-server without namespace in `server.py`
- Implement the following MCP tools with all parameters from the sync methods overview:
  - `list_document_types` — parameters: `ids`, `name_contains`, `name_exact`, `page`, `page_size`, `ordering`, `descending`
  - `get_document_type` — parameter: `id`
  - `create_document_type` — parameters: `name`, `match`, `matching_algorithm`, `is_insensitive`, `owner`, `set_permissions`
  - `update_document_type` — parameters: `id`, `name`, `match`, `matching_algorithm`, `is_insensitive`, `owner`, `set_permissions`
  - `delete_document_type` — parameter: `id`
  - `bulk_delete_document_types` — parameter: `ids`
  - `bulk_set_document_type_permissions` — parameters: `ids`, `set_permissions`, `owner`, `merge`
- Return types: `list_document_types` → `List[DocumentType]`; `get_document_type`, `create_document_type`, `update_document_type` → `DocumentType`; delete/bulk tools → `None`
- Tool names follow verb-first, singular/plural cardinality convention from CLAUDE.md
- UNSET sentinel used for all optional `update_document_type` parameters; `None` clears the field, omitting leaves it unchanged

### Out of Scope

- Changes to any other existing sub-server or resource
- Changes to transport configuration

---

## Acceptance Criteria

- [ ] `tools/document_types.py` exists and defines a `FastMCP` sub-server instance
- [ ] `server.py` mounts the document types sub-server without namespace alongside the existing sub-servers
- [ ] `list_document_types` is implemented with all 7 parameters (`ids`, `name_contains`, `name_exact`, `page`, `page_size`, `ordering`, `descending`) and returns `List[DocumentType]`
- [ ] `get_document_type` is implemented with parameter `id` and returns `DocumentType`
- [ ] `create_document_type` is implemented with all 6 parameters (`name`, `match`, `matching_algorithm`, `is_insensitive`, `owner`, `set_permissions`) and returns `DocumentType`
- [ ] `update_document_type` is implemented with all 7 parameters (`id` + the same 6 as create) and returns `DocumentType`; UNSET sentinel is used for all optional params so that `None` clears and omitting leaves unchanged
- [ ] `delete_document_type` is implemented with parameter `id` and returns `None`
- [ ] `bulk_delete_document_types` is implemented with parameter `ids: List[int]` and returns `None`
- [ ] `bulk_set_document_type_permissions` is implemented with parameters `ids`, `set_permissions`, `owner`, `merge` and returns `None`
- [ ] All 7 tools are registered and callable via the MCP server
- [ ] Tool names follow verb-first, singular/plural cardinality convention
- [ ] Return types use easypaperless Pydantic models directly (`DocumentType`)
- [ ] UNSET sentinel is used correctly for optional update parameters (distinguishes "not provided" from `None`)

---

## Dependencies & Constraints

- Depends on `easypaperless` package exposing all listed methods on `SyncPaperlessClient.document_types`
- `MatchingAlgorithm` and `SetPermissions` types must be imported from `easypaperless` as needed
- UNSET sentinel must be used for `update_document_type` parameters that support leave-unchanged semantics

---

## Priority

`High`

---

## Additional Notes

- easypaperless document types API reference: https://moritzgrenke.github.io/easypaperless/easypaperless/resources.html
- Pattern to follow: `tools/correspondents.py` and issue 0008
- `MatchingAlgorithm` enum values: `NONE | ANY_WORD | ALL_WORDS | EXACT | REGEX | FUZZY | AUTO`

---

## QA

**Tested by:** QA Engineer
**Date:** 2026-03-15
**Commit:** 016f7d4

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC: `tools/document_types.py` exists with `FastMCP` instance | File exists, `document_types = FastMCP("document_types")` | Confirmed at line 13 | ✅ Pass |
| 2 | AC: `server.py` mounts document types sub-server without namespace | `mcp.mount(document_types)` present | Confirmed at server.py:16 | ✅ Pass |
| 3 | AC: `list_document_types` has all 7 params and returns `List[DocumentType]` | All params present, correct return type | All 7 params confirmed; return type `list[DocumentType]` | ✅ Pass |
| 4 | AC: `get_document_type` has `id` param and returns `DocumentType` | Correct signature | Confirmed at line 59 | ✅ Pass |
| 5 | AC: `create_document_type` has all 6 params and returns `DocumentType` | All 6 params; correct return | All params present, return type correct | ✅ Pass |
| 6 | AC: `update_document_type` has all 7 params with UNSET sentinel | UNSET defaults for all optional params | Confirmed — all optional params default to `_UNSET`; `None` clears; omitting leaves unchanged | ✅ Pass |
| 7 | AC: `delete_document_type` has `id` param and returns `None` | `id: int`, `-> None` | Confirmed at line 162 | ✅ Pass |
| 8 | AC: `bulk_delete_document_types` has `ids: List[int]` and returns `None` | Correct signature | Confirmed at line 176 | ✅ Pass |
| 9 | AC: `bulk_set_document_type_permissions` has all 4 params and returns `None` | `ids`, `set_permissions`, `owner`, `merge`; `-> None` | Confirmed at line 189 | ✅ Pass |
| 10 | AC: All 7 tools registered and callable via MCP server | All decorated with `@document_types.tool` | All 7 decorators confirmed | ✅ Pass |
| 11 | AC: Tool names follow verb-first, singular/plural convention | e.g. `list_document_types`, `get_document_type` | All names compliant | ✅ Pass |
| 12 | AC: Return types use `DocumentType` Pydantic model directly | `DocumentType` returned | Confirmed for all 3 returning tools | ✅ Pass |
| 13 | AC: UNSET sentinel correctly distinguishes not-provided from None | `if x is not UNSET` gates forwarding | Logic verified in lines 146–157 | ✅ Pass |
| 14 | Edge: `list_document_types()` with no params omits all optional kwargs | No extra keys in client call | Unit test `test_list_document_types_omits_none_optional_params` passes | ✅ Pass |
| 15 | Edge: `update_document_type(1)` with only id sends no kwargs | Empty kwargs dict forwarded | Unit test `test_update_document_type_no_extra_kwargs_when_only_id` passes | ✅ Pass |
| 16 | Edge: `update_document_type` with `None` clears nullable fields | `match=None` forwarded as `None` | Unit test `test_update_document_type_clears_nullable_fields_when_none_passed` passes | ✅ Pass |
| 17 | Regression: existing sub-servers still mounted in server.py | documents, tags, correspondents, custom_fields still mounted | All 5 mounts confirmed in server.py | ✅ Pass |
| 18 | Integration: `list_document_types` returns list from live instance | `list` of `DocumentType` objects | 3 integration tests pass against live paperless-ngx | ✅ Pass |
| 19 | Integration: `get_document_type` round-trip fetches correct ID | Fetched ID matches listed ID | Integration test `test_get_document_type_round_trip` passes | ✅ Pass |
| 20 | Static analysis: ruff linting | No issues | `All checks passed!` | ✅ Pass |
| 21 | Static analysis: mypy strict type checking | No issues | `Success: no issues found in 1 source file` | ✅ Pass |

### Bugs Found

None.

### Automated Tests

- Suite: `tests/unit/test_document_types.py` — 30 passed, 0 failed
- Suite: `tests/integration/test_document_types.py` — 3 passed, 0 failed
- Note: 2 `PydanticJsonSchemaWarning` for non-serializable UNSET default — pre-existing, not introduced by this issue

### Summary

- ACs tested: 12/12
- ACs passing: 12/12
- Bugs found: 0
- Recommendation: ✅ Ready to merge
