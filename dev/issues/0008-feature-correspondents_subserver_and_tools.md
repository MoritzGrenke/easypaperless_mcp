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
