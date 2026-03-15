# easypaperless v0.2.0 – SyncPaperlessClient Methods Overview

> Sync client accessed via `SyncPaperlessClient`. Parameters are identical to the async counterparts.

---

## SyncPaperlessClient Constructor

```python
SyncPaperlessClient(url, api_key, **kwargs)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | — | Base URL of the paperless-ngx instance |
| `api_key` | `str` | — | API authentication token |
| `timeout` | `float` | `30.0` | Request timeout in seconds |
| `poll_interval` | `float` | `2.0` | Status check interval for upload polling (seconds) |
| `poll_timeout` | `float` | `60.0` | Max wait time for document processing (seconds) |

---

## client.documents — `SyncDocumentsResource`

### `get(id, *, include_metadata)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `int` | — | Numeric paperless-ngx document ID |
| `include_metadata` | `bool` | `False` | When `True`, fetches extended file-level metadata concurrently and attaches it to the document |

Returns: `Document`

---

### `get_metadata(id)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `int` | — | Numeric paperless-ngx document ID |

Returns: `DocumentMetadata`

---

### `list(...)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `search` | `str \| None` | `None` | Search string; behaviour depends on `search_mode` |
| `search_mode` | `str` | `"title_or_content"` | How `search` is applied: `"title_or_content"`, `"title"`, `"query"`, `"original_filename"` |
| `ids` | `List[int] \| None` | `None` | Return only documents whose ID is in this list |
| `tags` | `List[int\|str] \| None` | `None` | Documents must have **all** of these tags (AND semantics) |
| `any_tags` | `List[int\|str] \| None` | `None` | Documents must have **at least one** of these tags |
| `exclude_tags` | `List[int\|str] \| None` | `None` | Documents must have **none** of these tags |
| `correspondent` | `int\|str\|None\|UNSET` | `UNSET` | Filter to this correspondent; `None` returns only docs with no correspondent set |
| `any_correspondent` | `List[int\|str] \| None` | `None` | Filter to documents assigned to any of these correspondents |
| `exclude_correspondents` | `List[int\|str] \| None` | `None` | Exclude documents assigned to any of these correspondents |
| `document_type` | `int\|str\|None\|UNSET` | `UNSET` | Filter to this document type; `None` returns only docs with no type set |
| `document_type_name_contains` | `str \| None` | `None` | Case-insensitive substring filter on document type name |
| `document_type_name_exact` | `str \| None` | `None` | Case-insensitive exact match on document type name |
| `any_document_type` | `List[int\|str] \| None` | `None` | Filter to documents whose type is any of these |
| `exclude_document_types` | `List[int\|str] \| None` | `None` | Exclude documents whose type is any of these |
| `storage_path` | `int\|str\|None\|UNSET` | `UNSET` | Filter to this storage path; `None` returns only docs with no storage path set |
| `any_storage_paths` | `List[int\|str] \| None` | `None` | Filter to documents assigned to any of these storage paths |
| `exclude_storage_paths` | `List[int\|str] \| None` | `None` | Exclude documents assigned to any of these storage paths |
| `owner` | `int\|None\|UNSET` | `UNSET` | Filter to documents owned by this user ID; `None` returns only docs with no owner set |
| `exclude_owners` | `List[int] \| None` | `None` | Exclude documents owned by any of these user IDs |
| `custom_fields` | `List[int\|str] \| None` | `None` | Documents must have **all** of these custom fields set |
| `any_custom_fields` | `List[int\|str] \| None` | `None` | Documents must have **at least one** of these custom fields |
| `exclude_custom_fields` | `List[int\|str] \| None` | `None` | Documents must have **none** of these custom fields |
| `custom_field_query` | `List[Any] \| None` | `None` | Filter documents by custom field values (structured query) |
| `archive_serial_number` | `int\|None\|UNSET` | `UNSET` | Filter by exact archive serial number; `None` returns only docs with no ASN set |
| `archive_serial_number_from` | `int \| None` | `None` | Filter by ASN >= this value |
| `archive_serial_number_till` | `int \| None` | `None` | Filter by ASN <= this value |
| `created_after` | `date\|str\|None` | `None` | Only documents created after this date |
| `created_before` | `date\|str\|None` | `None` | Only documents created before this date |
| `added_after` | `date\|datetime\|str\|None` | `None` | Only documents added after this date/time (exclusive) |
| `added_from` | `date\|datetime\|str\|None` | `None` | Only documents added on or after this date/time (inclusive) |
| `added_before` | `date\|datetime\|str\|None` | `None` | Only documents added before this date/time (exclusive) |
| `added_until` | `date\|datetime\|str\|None` | `None` | Only documents added on or before this date/time (inclusive) |
| `modified_after` | `date\|datetime\|str\|None` | `None` | Only documents modified after this date/time (exclusive) |
| `modified_from` | `date\|datetime\|str\|None` | `None` | Only documents modified on or after this date/time (inclusive) |
| `modified_before` | `date\|datetime\|str\|None` | `None` | Only documents modified before this date/time (exclusive) |
| `modified_until` | `date\|datetime\|str\|None` | `None` | Only documents modified on or before this date/time (inclusive) |
| `checksum` | `str \| None` | `None` | MD5 checksum of the original file (exact match) |
| `page_size` | `int` | `25` | Number of results per API page |
| `page` | `int \| None` | `None` | Return only this specific page (1-based); omit to auto-paginate all results |
| `ordering` | `str \| None` | `None` | Field name to sort by |
| `descending` | `bool` | `False` | When `True`, reverses the sort direction |
| `max_results` | `int \| None` | `None` | Stop after collecting this many documents |
| `on_page` | `Callable[[int, int\|None], None] \| None` | `None` | Callback invoked after each page fetch; receives `(page_number, total_pages)` |

Returns: `List[Document]`

---

### `update(id, ...)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `int` | — | Numeric ID of the document to update |
| `title` | `str\|None\|UNSET` | `UNSET` | New document title |
| `content` | `str\|None\|UNSET` | `UNSET` | OCR text content of the document |
| `created` | `date\|str\|None\|UNSET` | `UNSET` | Creation date as ISO-8601 string or `date` object |
| `correspondent` | `int\|str\|None\|UNSET` | `UNSET` | Correspondent to assign (ID or name); `None` clears it |
| `document_type` | `int\|str\|None\|UNSET` | `UNSET` | Document type to assign (ID or name); `None` clears it |
| `storage_path` | `int\|str\|None\|UNSET` | `UNSET` | Storage path to assign (ID or name); `None` clears it |
| `tags` | `List[int\|str]\|None\|UNSET` | `UNSET` | Full replacement list of tags (IDs or names) |
| `archive_serial_number` | `int\|None\|UNSET` | `UNSET` | Archive serial number to assign; `None` clears it |
| `custom_fields` | `List[dict[str,Any]]\|None\|UNSET` | `UNSET` | List of `{"field": <field_id>, "value": ...}` dicts |
| `owner` | `int\|None\|UNSET` | `UNSET` | Numeric user ID to assign as owner; `None` clears it |
| `set_permissions` | `SetPermissions\|None\|UNSET` | `UNSET` | Explicit view/change permission sets |
| `remove_inbox_tags` | `bool\|None\|UNSET` | `UNSET` | When `True`, removes all inbox tags from the document |

Returns: `Document`

---

### `delete(id)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `int` | — | Numeric ID of the document to permanently delete |

Returns: `None`

---

### `download(id, *, original)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `int` | — | Numeric ID of the document to download |
| `original` | `bool` | `False` | `False` returns the archived PDF; `True` returns the original uploaded file |

Returns: `bytes`

---

### `upload(file, ...)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file` | `str\|Path` | — | Path to the file to upload |
| `title` | `str \| None` | `None` | Title to assign to the document |
| `created` | `date\|str\|None` | `None` | Creation date as ISO-8601 string or `date` object |
| `correspondent` | `int\|str\|None\|UNSET` | `UNSET` | Correspondent to assign (ID or name) |
| `document_type` | `int\|str\|None\|UNSET` | `UNSET` | Document type to assign (ID or name) |
| `storage_path` | `int\|str\|None\|UNSET` | `UNSET` | Storage path to assign (ID or name) |
| `tags` | `List[int\|str] \| None` | `None` | Tags to assign (IDs or names) |
| `archive_serial_number` | `int\|None\|UNSET` | `UNSET` | Archive serial number to assign |
| `custom_fields` | `List[dict[str,Any]] \| None` | `None` | List of `{"field": <field_id>, "value": ...}` dicts |
| `wait` | `bool` | `False` | `False` returns immediately with task ID; `True` polls until processing completes and returns `Document` |
| `poll_interval` | `float \| None` | `None` | Override client-level `poll_interval` (seconds) |
| `poll_timeout` | `float \| None` | `None` | Override client-level `poll_timeout` (seconds) |

Returns: `str` (Celery task ID) when `wait=False`, `Document` when `wait=True`

---

### Bulk Operations

| Method | Parameters | Description |
|--------|-----------|-------------|
| `bulk_add_tag(document_ids, tag)` | `document_ids: List[int]`, `tag: int\|str` | Add a tag (ID or name) to multiple documents |
| `bulk_remove_tag(document_ids, tag)` | `document_ids: List[int]`, `tag: int\|str` | Remove a tag (ID or name) from multiple documents |
| `bulk_modify_tags(document_ids, *, add_tags, remove_tags)` | `document_ids: List[int]`, `add_tags: List[int\|str]\|None=None`, `remove_tags: List[int\|str]\|None=None` | Add and/or remove tags atomically |
| `bulk_delete(document_ids)` | `document_ids: List[int]` | Permanently delete multiple documents |
| `bulk_set_correspondent(document_ids, correspondent)` | `document_ids: List[int]`, `correspondent: int\|str\|None` | Assign correspondent (ID or name); `None` clears |
| `bulk_set_document_type(document_ids, document_type)` | `document_ids: List[int]`, `document_type: int\|str\|None` | Assign document type (ID or name); `None` clears |
| `bulk_set_storage_path(document_ids, storage_path)` | `document_ids: List[int]`, `storage_path: int\|str\|None` | Assign storage path (ID or name); `None` clears |
| `bulk_modify_custom_fields(document_ids, *, add_fields, remove_fields)` | `document_ids: List[int]`, `add_fields: List[dict[str,Any]]\|None=None`, `remove_fields: List[int]\|None=None` | Add and/or remove custom field values |
| `bulk_set_permissions(document_ids, *, set_permissions, owner, merge)` | `document_ids: List[int]`, `set_permissions: SetPermissions\|None=None`, `owner: int\|None=None`, `merge: bool=False` | Set permissions/owner; `merge=True` merges with existing |

All bulk methods return `None`.

---

## client.documents.notes — `SyncNotesResource`

### `list(document_id)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `document_id` | `int` | — | Numeric ID of the document whose notes to retrieve |

Returns: `List[DocumentNote]` ordered by creation time

---

### `create(document_id, *, note)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `document_id` | `int` | — | Numeric ID of the document to annotate |
| `note` | `str` | — | Text content of the note |

Returns: `DocumentNote`

---

### `delete(document_id, note_id)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `document_id` | `int` | — | Numeric ID of the document that owns the note |
| `note_id` | `int` | — | Numeric ID of the note to delete |

Returns: `None`

---

## client.tags — `SyncTagsResource`

### `list(...)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ids` | `List[int] \| None` | `None` | Return only tags whose ID is in this list |
| `name_contains` | `str \| None` | `None` | Case-insensitive substring filter on tag name |
| `name_exact` | `str \| None` | `None` | Case-insensitive exact match on tag name |
| `page` | `int \| None` | `None` | Return only this specific page (1-based) |
| `page_size` | `int \| None` | `None` | Number of results per page |
| `ordering` | `str \| None` | `None` | Field to sort by |
| `descending` | `bool` | `False` | When `True`, reverses the sort direction |

Returns: `List[Tag]`

---

### `get(id)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `int` | — | Numeric tag ID |

Returns: `Tag`

---

### `create(...)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | — | Tag name. Must be unique |
| `color` | `str\|None\|UNSET` | `UNSET` | Background colour as a CSS hex string |
| `is_inbox_tag` | `bool\|None\|UNSET` | `UNSET` | When `True`, newly ingested documents automatically get this tag |
| `match` | `str\|None\|UNSET` | `UNSET` | Auto-matching pattern |
| `matching_algorithm` | `MatchingAlgorithm\|None\|UNSET` | `UNSET` | Controls how `match` is applied |
| `is_insensitive` | `bool` | `True` | When `True`, `match` is case-insensitive |
| `parent` | `int\|None\|UNSET` | `UNSET` | ID of parent tag for hierarchical trees |
| `owner` | `int\|None\|UNSET` | `UNSET` | Numeric user ID to assign as owner |
| `set_permissions` | `SetPermissions \| None` | `None` | Explicit view/change permission sets |

Returns: `Tag`

---

### `update(id, ...)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `int` | — | Numeric ID of the tag to update |
| `name` | `str\|None\|UNSET` | `UNSET` | Tag name |
| `color` | `str\|None\|UNSET` | `UNSET` | Background colour as a CSS hex string |
| `is_inbox_tag` | `bool\|None\|UNSET` | `UNSET` | When `True`, newly ingested documents get this tag |
| `match` | `str\|None\|UNSET` | `UNSET` | Auto-matching pattern |
| `matching_algorithm` | `MatchingAlgorithm\|None\|UNSET` | `UNSET` | Controls how `match` is applied |
| `is_insensitive` | `bool\|None\|UNSET` | `UNSET` | When `True`, `match` is case-insensitive |
| `parent` | `int\|None\|UNSET` | `UNSET` | ID of parent tag; `None` makes it a root tag |
| `owner` | `int\|None\|UNSET` | `UNSET` | Numeric user ID; `None` clears; UNSET leaves unchanged |
| `set_permissions` | `SetPermissions\|None\|UNSET` | `UNSET` | Explicit view/change permission sets; UNSET leaves unchanged |

Returns: `Tag`

---

### `delete(id)` / `bulk_delete(ids)` / `bulk_set_permissions(ids, ...)`

| Method | Parameters | Description |
|--------|-----------|-------------|
| `delete(id)` | `id: int` | Delete a tag |
| `bulk_delete(ids)` | `ids: List[int]` | Permanently delete multiple tags |
| `bulk_set_permissions(ids, *, set_permissions, owner, merge)` | `ids: List[int]`, `set_permissions: SetPermissions\|None=None`, `owner: int\|None=None`, `merge: bool=False` | Set permissions/owner; `merge=True` merges with existing |

All return `None`.

---

## client.correspondents — `SyncCorrespondentsResource`

### `list(...)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ids` | `List[int] \| None` | `None` | Return only correspondents whose ID is in this list |
| `name_contains` | `str \| None` | `None` | Case-insensitive substring filter on name |
| `name_exact` | `str \| None` | `None` | Case-insensitive exact match on name |
| `page` | `int \| None` | `None` | Return only this specific page (1-based) |
| `page_size` | `int \| None` | `None` | Number of results per page |
| `ordering` | `str \| None` | `None` | Field to sort by |
| `descending` | `bool` | `False` | When `True`, reverses the sort direction |

Returns: `List[Correspondent]`

---

### `get(id)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `int` | — | Numeric correspondent ID |

Returns: `Correspondent`

---

### `create(...)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | — | Correspondent name. Must be unique |
| `match` | `str\|None\|UNSET` | `UNSET` | Auto-matching pattern |
| `matching_algorithm` | `MatchingAlgorithm\|None\|UNSET` | `UNSET` | Controls how `match` is applied |
| `is_insensitive` | `bool` | `True` | When `True`, `match` is case-insensitive |
| `owner` | `int\|None\|UNSET` | `UNSET` | Numeric user ID to assign as owner |
| `set_permissions` | `SetPermissions \| None` | `None` | Explicit view/change permission sets |

Returns: `Correspondent`

---

### `update(id, ...)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `int` | — | Numeric ID of the correspondent to update |
| `name` | `str\|None\|UNSET` | `UNSET` | Correspondent name |
| `match` | `str\|None\|UNSET` | `UNSET` | Auto-matching pattern |
| `matching_algorithm` | `MatchingAlgorithm\|None\|UNSET` | `UNSET` | Controls how `match` is applied |
| `is_insensitive` | `bool\|None\|UNSET` | `UNSET` | When `True`, `match` is case-insensitive |
| `owner` | `int\|None\|UNSET` | `UNSET` | Numeric user ID; `None` clears; UNSET leaves unchanged |
| `set_permissions` | `SetPermissions\|None\|UNSET` | `UNSET` | Explicit view/change permission sets; UNSET leaves unchanged |

Returns: `Correspondent`

---

### `delete(id)` / `bulk_delete(ids)` / `bulk_set_permissions(ids, ...)`

| Method | Parameters | Description |
|--------|-----------|-------------|
| `delete(id)` | `id: int` | Delete a correspondent |
| `bulk_delete(ids)` | `ids: List[int]` | Permanently delete multiple correspondents |
| `bulk_set_permissions(ids, *, set_permissions, owner, merge)` | `ids: List[int]`, `set_permissions: SetPermissions\|None=None`, `owner: int\|None=None`, `merge: bool=False` | Set permissions/owner; `merge=True` merges with existing |

All return `None`.

---

## client.document_types — `SyncDocumentTypesResource`

### `list(...)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ids` | `List[int] \| None` | `None` | Return only document types whose ID is in this list |
| `name_contains` | `str \| None` | `None` | Case-insensitive substring filter on name |
| `name_exact` | `str \| None` | `None` | Case-insensitive exact match on name |
| `page` | `int \| None` | `None` | Return only this specific page (1-based) |
| `page_size` | `int \| None` | `None` | Number of results per page |
| `ordering` | `str \| None` | `None` | Field to sort by |
| `descending` | `bool` | `False` | When `True`, reverses the sort direction |

Returns: `List[DocumentType]`

---

### `get(id)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `int` | — | Numeric document-type ID |

Returns: `DocumentType`

---

### `create(...)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | — | Document-type name. Must be unique |
| `match` | `str\|None\|UNSET` | `UNSET` | Auto-matching pattern |
| `matching_algorithm` | `MatchingAlgorithm\|None\|UNSET` | `UNSET` | Controls how `match` is applied |
| `is_insensitive` | `bool` | `True` | When `True`, `match` is case-insensitive |
| `owner` | `int\|None\|UNSET` | `UNSET` | Numeric user ID to assign as owner |
| `set_permissions` | `SetPermissions \| None` | `None` | Explicit view/change permission sets |

Returns: `DocumentType`

---

### `update(id, ...)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `int` | — | Numeric ID of the document type to update |
| `name` | `str\|None\|UNSET` | `UNSET` | Document-type name |
| `match` | `str\|None\|UNSET` | `UNSET` | Auto-matching pattern |
| `matching_algorithm` | `MatchingAlgorithm\|None\|UNSET` | `UNSET` | Controls how `match` is applied |
| `is_insensitive` | `bool\|None\|UNSET` | `UNSET` | When `True`, `match` is case-insensitive |
| `owner` | `int\|None\|UNSET` | `UNSET` | Numeric user ID; `None` clears; UNSET leaves unchanged |
| `set_permissions` | `SetPermissions\|None\|UNSET` | `UNSET` | Explicit view/change permission sets; UNSET leaves unchanged |

Returns: `DocumentType`

---

### `delete(id)` / `bulk_delete(ids)` / `bulk_set_permissions(ids, ...)`

| Method | Parameters | Description |
|--------|-----------|-------------|
| `delete(id)` | `id: int` | Delete a document type |
| `bulk_delete(ids)` | `ids: List[int]` | Permanently delete multiple document types |
| `bulk_set_permissions(ids, *, set_permissions, owner, merge)` | `ids: List[int]`, `set_permissions: SetPermissions\|None=None`, `owner: int\|None=None`, `merge: bool=False` | Set permissions/owner; `merge=True` merges with existing |

All return `None`.

---

## client.custom_fields — `SyncCustomFieldsResource`

> Note: no `bulk_delete` or `bulk_set_permissions` on this resource.

### `list(...)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name_contains` | `str \| None` | `None` | Case-insensitive substring filter on name |
| `name_exact` | `str \| None` | `None` | Case-insensitive exact match on name |
| `page` | `int \| None` | `None` | Return only this specific page (1-based) |
| `page_size` | `int \| None` | `None` | Number of results per page |
| `ordering` | `str \| None` | `None` | Field to sort by |
| `descending` | `bool` | `False` | When `True`, reverses the sort direction |

Returns: `List[CustomField]`

---

### `get(id)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `int` | — | Numeric custom-field ID |

Returns: `CustomField`

---

### `create(...)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | — | Field name shown in the UI. Must be unique |
| `data_type` | `str` | — | Value type: `"string"`, `"boolean"`, `"integer"`, `"float"`, `"monetary"`, `"date"`, `"url"`, `"documentlink"`, `"select"` |
| `extra_data` | `Any \| None` | `None` | Additional configuration for the field type |
| `owner` | `int\|None\|UNSET` | `UNSET` | Numeric user ID to assign as owner |
| `set_permissions` | `SetPermissions \| None` | `None` | Explicit view/change permission sets |

Returns: `CustomField`

---

### `update(id, ...)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `int` | — | Numeric ID of the custom field to update |
| `name` | `str\|None\|UNSET` | `UNSET` | Field name shown in the UI |
| `data_type` | `str\|None\|UNSET` | `UNSET` | Value type; UNSET leaves unchanged |
| `extra_data` | `Any\|None\|UNSET` | `UNSET` | Additional configuration for the field type |

Returns: `CustomField`

---

### `delete(id)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `int` | — | Numeric ID of the custom field to delete |

Returns: `None`

---

## client.storage_paths — `SyncStoragePathsResource`

### `list(...)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ids` | `List[int] \| None` | `None` | Return only storage paths whose ID is in this list |
| `name_contains` | `str \| None` | `None` | Case-insensitive substring filter on name |
| `name_exact` | `str \| None` | `None` | Case-insensitive exact match on name |
| `path_contains` | `str \| None` | `None` | Case-insensitive substring filter on path template |
| `path_exact` | `str \| None` | `None` | Case-insensitive exact match on path template |
| `page` | `int \| None` | `None` | Return only this specific page (1-based) |
| `page_size` | `int \| None` | `None` | Number of results per page |
| `ordering` | `str \| None` | `None` | Field to sort by |
| `descending` | `bool` | `False` | When `True`, reverses the sort direction |

Returns: `List[StoragePath]`

---

### `get(id)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `int` | — | Numeric storage-path ID |

Returns: `StoragePath`

---

### `create(...)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | — | Storage-path name. Must be unique |
| `path` | `str \| None` | `None` | Template string for the archive file path |
| `match` | `str\|None\|UNSET` | `UNSET` | Auto-matching pattern |
| `matching_algorithm` | `MatchingAlgorithm\|None\|UNSET` | `UNSET` | Controls how `match` is applied |
| `is_insensitive` | `bool` | `True` | When `True`, `match` is case-insensitive |
| `owner` | `int\|None\|UNSET` | `UNSET` | Numeric user ID to assign as owner |
| `set_permissions` | `SetPermissions \| None` | `None` | Explicit view/change permission sets |

Returns: `StoragePath`

---

### `update(id, ...)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `int` | — | Numeric ID of the storage path to update |
| `name` | `str\|None\|UNSET` | `UNSET` | Storage-path name |
| `path` | `str\|None\|UNSET` | `UNSET` | Template string for the archive file path |
| `match` | `str\|None\|UNSET` | `UNSET` | Auto-matching pattern |
| `matching_algorithm` | `MatchingAlgorithm\|None\|UNSET` | `UNSET` | Controls how `match` is applied |
| `is_insensitive` | `bool\|None\|UNSET` | `UNSET` | When `True`, `match` is case-insensitive |
| `owner` | `int\|None\|UNSET` | `UNSET` | Numeric user ID; `None` clears; UNSET leaves unchanged |
| `set_permissions` | `SetPermissions\|None\|UNSET` | `UNSET` | Explicit view/change permission sets; UNSET leaves unchanged |

Returns: `StoragePath`

---

### `delete(id)` / `bulk_delete(ids)` / `bulk_set_permissions(ids, ...)`

| Method | Parameters | Description |
|--------|-----------|-------------|
| `delete(id)` | `id: int` | Delete a storage path |
| `bulk_delete(ids)` | `ids: List[int]` | Permanently delete multiple storage paths |
| `bulk_set_permissions(ids, *, set_permissions, owner, merge)` | `ids: List[int]`, `set_permissions: SetPermissions\|None=None`, `owner: int\|None=None`, `merge: bool=False` | Set permissions/owner; `merge=True` merges with existing |

All return `None`.

---

## Enums & Shared Types

### `MatchingAlgorithm`
`NONE | ANY_WORD | ALL_WORDS | EXACT | REGEX | FUZZY | AUTO`

### `FieldDataType` (for `custom_fields.create`)
`string | boolean | integer | float | monetary | date | url | documentlink | select`

### `SetPermissions`
Pydantic model representing user/group view and change permission sets.

### UNSET Sentinel
Parameters typed `| UNSET` use a sentinel to distinguish "not provided" from `None`.
- Passing `None` → clears / sets the field to null
- Omitting / passing `UNSET` → field is left unchanged (relevant for `update` calls)
