# [FEATURE] Documents sub-server with full resource tool coverage

## Summary

Restructure the existing monolithic `server.py` into the proper layered architecture defined in CLAUDE.md, and deliver a complete MCP tool set for the documents resource. This replaces the current placeholder implementation with production-ready tools that cover every operation exposed by the `easypaperless` documents API — including bulk operations and field-filtered responses.

---

## Problem Statement

The current codebase has all logic in a single `server.py` with only three rudimentary tools (`list_documents`, `get_document`, `search_documents`). Two of those tools are duplicates of each other. The project structure defined in CLAUDE.md (separate `client.py`, `tools/` sub-servers per resource) has not been established yet. Without this foundation, the remaining resource modules cannot be added cleanly.

Additionally, the document tools return either only titles or full model dumps, providing no token-efficient middle ground for AI agents working with large document sets.

---

## Proposed Solution

Refactor the codebase to match the target project structure, then implement all methods of the `easypaperless` documents resource as MCP tools on a dedicated `tools/documents.py` sub-server.

The sub-server is mounted without namespace in `server.py`. A `client.py` module provides the `get_client()` singleton. The `search_documents` tool is removed as a duplicate.

Two tools (`list_documents`, `get_document`) receive a `return_fields` parameter that restricts which fields are included in the response — all other fields are set to `None` before returning — allowing AI agents to request only the data they need.

The `download` tool is explicitly excluded.

---

## User Stories

- As an AI agent, I want to list documents with only the fields I need so that I don't waste context window on irrelevant data.
- As an AI agent, I want to get detailed information about a single document with a configurable field selection so that I can retrieve richer data on demand.
- As an AI agent, I want to update, delete, upload, and manage metadata for individual documents so that I can maintain a paperless-ngx instance.
- As an AI agent, I want to perform bulk tag, correspondent, document type, storage path, custom field, and permission operations so that I can efficiently process large document collections.

---

## Scope

### In Scope

- Restructure: extract `get_client()` singleton into `src/easypaperless_mcp/client.py`
- Restructure: create `src/easypaperless_mcp/tools/__init__.py` (empty)
- Restructure: create `src/easypaperless_mcp/tools/documents.py` with its own `FastMCP` sub-server instance
- Restructure: update `server.py` to import and mount the documents sub-server; remove inline tool definitions and `get_client()`
- Remove: `search_documents` tool (duplicate of `list_documents`)
- Implement individual document tools:
  - `list_documents` — filters: title, content, tags, dates, correspondent, document type, storage path, ordering, search, max_results; `return_fields` parameter (see defaults below)
  - `get_document` — by ID; `return_fields` parameter (see defaults below)
  - `get_document_metadata` — file-level technical metadata (checksums, sizes, MIME types)
  - `update_document` — partial update via PATCH semantics; supports UNSET fields
  - `delete_document` — permanently remove a document
  - `upload_document` — upload a file; optionally wait for processing task completion
- Implement bulk document tools:
  - `bulk_add_tag`
  - `bulk_remove_tag`
  - `bulk_modify_tags`
  - `bulk_delete_documents`
  - `bulk_set_correspondent`
  - `bulk_set_document_type`
  - `bulk_set_storage_path`
  - `bulk_modify_custom_fields`
  - `bulk_set_permissions`
- `return_fields` for `list_documents` defaults to: `["id", "title", "created", "correspondent", "document_type", "tags", "archive_serial_number"]`
- `return_fields` for `get_document` defaults to: `["id", "title", "created", "correspondent", "document_type", "storage_path", "tags", "custom_fields", "notes", "archive_serial_number", "original_file_name", "page_count"]`
- Fields not listed in `return_fields` are set to `None` on the returned model before serialization

### Out of Scope

- `download_document` tool — not implemented by design
- Tools for any other resource (tags, correspondents, etc.) — separate issues
- Changes to transport configuration or environment variable handling

---

## Acceptance Criteria

- [ ] `client.py` exists and exports `get_client() -> SyncPaperlessClient`
- [ ] `tools/__init__.py` exists
- [ ] `tools/documents.py` defines a `FastMCP` sub-server instance and all tools listed above
- [ ] `server.py` mounts the documents sub-server without namespace and no longer contains inline tool definitions or `get_client()`
- [ ] `search_documents` tool is removed and no longer registered
- [ ] `list_documents` accepts a `return_fields: list[str]` parameter with the specified default; fields absent from the list are set to `None` on the returned document objects
- [ ] `get_document` accepts a `return_fields: list[str]` parameter with the specified default; fields absent from the list are set to `None` on the returned document object
- [ ] All 6 individual document tools (`list_documents`, `get_document`, `get_document_metadata`, `update_document`, `delete_document`, `upload_document`) are registered and callable
- [ ] All 9 bulk operation tools are registered and callable
- [ ] Tool names follow verb-first, singular/plural cardinality convention from CLAUDE.md
- [ ] Return types use easypaperless Pydantic models directly where meaningful
- [ ] No tool named `download_document` exists

---

## Dependencies & Constraints

- Depends on `easypaperless` package exposing all listed methods on `SyncPaperlessClient.documents`
- `return_fields` filtering must set non-listed fields to `None` (not omit them from the schema), so the Pydantic model remains valid and fully typed
- UNSET semantics for `update_document` must be handled in line with how `easypaperless` exposes them (likely a sentinel value)

---

## Priority

`High`

---

## Additional Notes

- easypaperless documents API reference: https://moritzgrenke.github.io/easypaperless/easypaperless/resources.html
- The `return_fields` mechanism is the primary context-saving measure described in the PRD. Keeping defaults narrow prevents accidental large responses from agents that do not explicitly request more fields.
