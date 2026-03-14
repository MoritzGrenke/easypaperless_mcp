# [FEATURE] Full parameter coverage for list_documents tool

## Summary

The `list_documents` MCP tool currently exposes only 10 of the 45 parameters supported by `easypaperless.documents.list()`. This prevents AI agents from using the full filtering, pagination, and ordering capabilities of paperless-ngx when listing documents.

---

## Problem Statement

When issue 0001 was implemented, `list_documents` received a subset of `documents.list()` parameters. The remaining ~35 parameters — covering tag exclusion, "any of" semantics, document type/storage path/correspondent alternatives, owner filtering, custom field queries, archive serial number ranges, added/modified date filtering, checksum lookup, and full pagination control — are inaccessible to AI agents. This significantly limits the ability to build precise queries against large document archives.

---

## Proposed Solution

Expose all remaining meaningful parameters of `easypaperless.documents.list()` as named parameters on the `list_documents` MCP tool. The `on_page` callback parameter is excluded as it is internal/streaming infrastructure not useful to AI agents.

Group additions by category:

**Document ID filtering:**
- `ids: list[int] | None` — restrict to a specific set of document IDs

**Tag filtering:**
- `any_tags: list[int | str] | None` — documents that have ANY of these tags
- `exclude_tags: list[int | str] | None` — documents that have NONE of these tags

**Correspondent filtering:**
- `any_correspondent: list[int | str] | None` — documents with any of these correspondents
- `exclude_correspondents: list[int | str] | None` — documents not matching these correspondents

**Document type filtering:**
- `document_type_name_contains: str | None` — document type name contains this string
- `document_type_name_exact: str | None` — document type name exact match
- `any_document_type: list[int | str] | None` — documents of any of these types
- `exclude_document_types: list[int | str] | None` — documents not of these types

**Storage path filtering:**
- `any_storage_paths: list[int | str] | None` — documents in any of these storage paths
- `exclude_storage_paths: list[int | str] | None` — documents not in these storage paths

**Owner filtering:**
- `owner: int | None` — documents owned by this user ID
- `exclude_owners: list[int] | None` — documents not owned by these user IDs

**Custom field filtering:**
- `custom_fields: list[int | str] | None` — documents with ALL of these custom fields set
- `any_custom_fields: list[int | str] | None` — documents with ANY of these custom fields set
- `exclude_custom_fields: list[int | str] | None` — documents with NONE of these custom fields set
- `custom_field_query: list[Any] | None` — advanced custom field query expression

**Archive serial number filtering:**
- `archive_serial_number: int | None` — exact ASN match
- `archive_serial_number_from: int | None` — ASN range start (inclusive)
- `archive_serial_number_till: int | None` — ASN range end (inclusive)

**Added date filtering:**
- `added_after: str | None` — documents added after this datetime (ISO string)
- `added_before: str | None` — documents added before this datetime (ISO string)

**Modified date filtering:**
- `modified_after: str | None` — documents last modified after this datetime (ISO string)
- `modified_before: str | None` — documents last modified before this datetime (ISO string)

**File checksum:**
- `checksum: str | None` — find document by exact file checksum

**Pagination & ordering:**
- `page: int | None` — page number for manual pagination
- `page_size: int` — number of results per page (default 25)
- `descending: bool` — reverse the ordering direction (default False)

---

## User Stories

- As an AI agent, I want to filter documents by "any of" tag/correspondent/type semantics so that I can build OR-style queries.
- As an AI agent, I want to exclude documents with specific tags, correspondents, or types so that I can narrow results without enumerating everything I want.
- As an AI agent, I want to filter by custom field presence and values so that I can query documents based on structured metadata.
- As an AI agent, I want to filter by added and modified dates so that I can find recently ingested or recently changed documents.
- As an AI agent, I want to control pagination explicitly so that I can page through large result sets efficiently.
- As an AI agent, I want to look up a document by checksum so that I can detect duplicates or verify a specific file.

---

## Scope

### In Scope

- Add all parameters listed in the Proposed Solution section to `list_documents` in `tools/documents.py`
- Each new parameter passes through to `documents.list()` only when explicitly provided (not `None`)
- The `added_after/before` and `modified_after/before` parameters accept ISO datetime strings (the easypaperless wrapper accepts `str`)
- Deprecate the redundant `added_from`, `added_until`, `modified_from`, `modified_until` aliases — expose only `added_after/before` and `modified_after/before` (the canonical names)
- Update docstring to document all new parameters
- Update unit tests to cover new parameters

### Out of Scope

- `on_page` callback — internal streaming mechanism, not meaningful as an MCP tool parameter
- Changes to any tool other than `list_documents`
- Changes to other resource modules (tags, correspondents, etc.)

---

## Acceptance Criteria

- [ ] `list_documents` accepts all parameters listed in the Proposed Solution section
- [ ] Each new parameter defaults to `None` (or appropriate default) and is only passed to `documents.list()` when not `None`
- [ ] `ids` parameter correctly restricts results to the given document IDs
- [ ] `any_tags` and `exclude_tags` parameters work alongside the existing `tags` parameter
- [ ] `any_correspondent`, `exclude_correspondents`, `any_document_type`, `exclude_document_types`, `any_storage_paths`, `exclude_storage_paths` are all functional
- [ ] `owner` and `exclude_owners` filter by user ownership
- [ ] `custom_fields`, `any_custom_fields`, `exclude_custom_fields`, `custom_field_query` are all passed through correctly
- [ ] `archive_serial_number`, `archive_serial_number_from`, `archive_serial_number_till` support exact and range ASN filtering
- [ ] `added_after`, `added_before`, `modified_after`, `modified_before` accept ISO datetime strings and filter correctly
- [ ] `checksum` allows lookup by exact file checksum
- [ ] `page`, `page_size`, `descending` give full pagination and ordering control
- [ ] `on_page` is NOT exposed as a tool parameter
- [ ] All existing parameters remain unchanged and continue to work
- [ ] Tool docstring documents every parameter
- [ ] Unit tests cover the new parameters (at least parameter pass-through assertions)

---

## Dependencies & Constraints

- Depends on `easypaperless >= 2.0` exposing all listed parameters on `documents.list()`
- `custom_field_query` accepts `list[Any]` as per the easypaperless signature; document its expected structure in the docstring
- The `archive_serial_number` parameter in `list_documents` must be handled separately from the existing `archive_serial_number` in `update_document` (different tools, no conflict)

---

## Priority

`High`

---

## Additional Notes

- easypaperless documents API reference: https://moritzgrenke.github.io/easypaperless/easypaperless/resources.html
- The full `list()` signature was verified from `.venv/Lib/site-packages/easypaperless/_internal/resources/documents.py`
- The alias parameters (`added_from`, `added_until`, `modified_from`, `modified_until`) exist in easypaperless but are redundant with `added_after/before` and `modified_after/before` — only the canonical forms should be exposed
