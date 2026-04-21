# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

#### Documents (Breaking)
- `list_documents` and `get_document` — `omitted_fields` now contains **only field name strings**. The retrieval hint is no longer appended as the last element of the list. Callers that read the final element of `omitted_fields` as the hint must switch to the new `omitted_fields_hint` field.

#### Documents (Additive)
- `list_documents` (`ListResult`) and `get_document` — new `omitted_fields_hint` field (string) carries the retrieval hint separately from `omitted_fields`. Present whenever one or more fields are omitted; empty string otherwise.
- `update_document` — new `return_fields: list[str] | None` parameter. Defaults to a smart set containing `id`, `modified`, and every field explicitly provided in the call. Explicit `return_fields` overrides the default entirely; `id` is always included. Response is now a filtered dict instead of the full `Document` model, with `omitted_fields` and `omitted_fields_hint` metadata following the same contract as `get_document`.

---

## [0.3.0] - 2026-04-21

### Changed

#### Documents (Breaking)
- `list_documents` items no longer contain keys for omitted fields — fields excluded via `return_fields` are now entirely absent from each item dict instead of being present as `null` or a zero value. Callers that relied on the full document shape being present (with nulls for unselected fields) must update their handling.
- `get_document` response no longer contains keys for omitted fields — same behaviour as above for the single-document endpoint.

#### Documents (Additive)
- `list_documents` — `ListResult` now includes an `omitted_fields` list that names every field excluded by `return_fields` and appends a retrieval hint. Empty when all fields are included.
- `get_document` — response dict now includes an `omitted_fields` key under the same conditions.
- `update_document` — new `add_tags` and `remove_tags` parameters for incremental tag changes without knowing the document's current tag list. Both accept IDs or names (strings are resolved via the tags API). Mutually exclusive with the existing `tags` parameter.

### Fixed

- `update_document` — the existing `tags` docstring now prominently warns that it **overwrites all existing tags** and recommends `add_tags` / `remove_tags` for incremental changes.

## [0.2.0] - 2026-03-20

### Added

#### Users
- `list_users` — list with username filtering, ordering, and pagination.
- `get_user` — fetch a single user by ID.
- `create_user` — create a user account with optional email, password, name, role flags, and group/permission assignments.
- `update_user` — PATCH semantics; pass `None` to clear nullable fields.
- `delete_user` — permanently delete a user account.

#### Trash
- `list_trash` — list all documents currently in the trash with pagination.
- `restore_trash` — restore one or more trashed documents back to active status.
- `empty_trash` — permanently and irreversibly delete specific documents from the trash.

#### Security
- Client-side authentication: `PAPERLESS_TOKEN` is now resolved per request from the MCP client (env var for stdio, HTTP headers for HTTP transport). The token is never read from the server environment.
- HTTP transport now accepts `Authorization: Bearer <token>` as the preferred auth header; `X-Paperless-Token` continues to work but is deprecated — a warning is logged when used.
- If both `Authorization: Bearer` and `X-Paperless-Token` are present, `Authorization: Bearer` takes precedence.
- `PAPERLESS_URL` can optionally be locked server-side (Docker); if not set, each client supplies it via `X-Paperless-URL` header.
- `CredentialMiddleware` injected into the FastMCP server to handle per-request credential resolution.

### Infrastructure
- RC release workflow added to GitHub Actions.
- Stable release workflow excludes pre-release tags.

## [0.1.0] - 2026-03-19

Initial release of easypaperless-mcp.

### Added

#### Documents
- `list_documents` — list with full filtering coverage (search, tags, correspondents, document types, storage paths, custom fields, date ranges, ASN, checksum, pagination, ordering). Compact default field set (`id`, `title`, `created`, `search_hit`) to keep token usage low; customisable via `return_fields`.
- `get_document` — fetch a single document with configurable `return_fields`; optional `include_metadata` flag.
- `get_document_metadata` — fetch file-level technical metadata (checksums, MIME type, page count, embedded PDF tags).
- `update_document` — PATCH semantics; omit a field to leave it unchanged, pass `None` to clear nullable fields (`correspondent`, `document_type`, `storage_path`, `archive_serial_number`, `owner`).
- `delete_document` — permanently delete a single document.
- `upload_document` — upload a file; `wait=True` polls until processing completes and returns the Document.
- `bulk_add_tag` / `bulk_remove_tag` — add or remove a single tag across many documents.
- `bulk_modify_tags` — atomically add and/or remove tags across many documents.
- `bulk_delete_documents` — permanently delete multiple documents.
- `bulk_set_correspondent` — assign or clear a correspondent across many documents.
- `bulk_set_document_type` — assign or clear a document type across many documents.
- `bulk_set_storage_path` — assign or clear a storage path across many documents.
- `bulk_modify_custom_fields` — add and/or remove custom field values across many documents.
- `bulk_set_permissions` — set owner and permissions across many documents.

#### Document Notes
- `list_document_notes` — list notes for a document with pagination.
- `create_document_note` — add a new note to a document.
- `delete_document_note` — delete a note from a document.

#### Tags
- `list_tags` — list with name filtering, ordering, and pagination.
- `get_tag` — fetch a single tag.
- `create_tag` — create a tag with optional auto-matching, colour, inbox flag, and hierarchy.
- `update_tag` — PATCH semantics; pass `None` to clear nullable fields.
- `delete_tag` — permanently delete a tag.
- `bulk_delete_tags` — permanently delete multiple tags.
- `bulk_set_tag_permissions` — set owner and permissions across many tags.

#### Correspondents
- `list_correspondents` — list with name filtering, ordering, and pagination.
- `get_correspondent` — fetch a single correspondent.
- `create_correspondent` — create a correspondent with optional auto-matching.
- `update_correspondent` — PATCH semantics; pass `None` to clear nullable fields.
- `delete_correspondent` — permanently delete a correspondent.
- `bulk_delete_correspondents` — permanently delete multiple correspondents.
- `bulk_set_correspondent_permissions` — set owner and permissions across many correspondents.

#### Document Types
- `list_document_types` — list with name filtering, ordering, and pagination.
- `get_document_type` — fetch a single document type.
- `create_document_type` — create a document type with optional auto-matching.
- `update_document_type` — PATCH semantics; pass `None` to clear nullable fields.
- `delete_document_type` — permanently delete a document type.
- `bulk_delete_document_types` — permanently delete multiple document types.
- `bulk_set_document_type_permissions` — set owner and permissions across many document types.

#### Custom Fields
- `list_custom_fields` — list with name filtering, ordering, and pagination.
- `get_custom_field` — fetch a single custom field.
- `create_custom_field` — create a custom field (string, boolean, integer, float, monetary, date, url, documentlink, select).
- `update_custom_field` — PATCH semantics; pass `None` to clear nullable fields.
- `delete_custom_field` — permanently delete a custom field.

#### Storage Paths
- `list_storage_paths` — list with name and path template filtering, ordering, and pagination.
- `get_storage_path` — fetch a single storage path.
- `create_storage_path` — create a storage path with optional auto-matching.
- `update_storage_path` — PATCH semantics; pass `None` to clear nullable fields.
- `delete_storage_path` — permanently delete a storage path.
- `bulk_delete_storage_paths` — permanently delete multiple storage paths.
- `bulk_set_storage_path_permissions` — set owner and permissions across many storage paths.

#### Infrastructure
- `stdio` and `streamable-http` transports controlled via `MCP_TRANSPORT` environment variable.
- Docker support: `Dockerfile` and `docker-compose.yml` for containerised deployment.
- GitHub Actions CI/CD release workflow.
- `ListResult[T]` response wrapper with `count` (total matches in paperless-ngx) and `items` for all `list_*` tools.
- `_filter_fields` helper ensures `return_fields` filtering never sets required fields to `None` (uses type-appropriate zero values instead).
- Singleton `SyncPaperlessClient` via `get_client()`.
