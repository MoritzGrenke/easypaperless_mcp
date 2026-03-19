# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
