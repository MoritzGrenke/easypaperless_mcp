# Tool Reference (59 tools)

## `bulk_add_tag`

Add a tag to multiple documents in a single request.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ids` | `array` | yes |  |
| `tag` | `integer` | yes |  |

## `bulk_delete_correspondents`

Permanently delete multiple correspondents in a single request.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ids` | `array` | yes |  |

## `bulk_delete_document_types`

Permanently delete multiple document types in a single request.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ids` | `array` | yes |  |

## `bulk_delete_documents`

Permanently delete multiple documents in a single request.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ids` | `array` | yes |  |

## `bulk_delete_storage_paths`

Permanently delete multiple storage paths in a single request.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ids` | `array` | yes |  |

## `bulk_delete_tags`

Permanently delete multiple tags in a single request.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ids` | `array` | yes |  |

## `bulk_modify_custom_fields`

Add and/or remove custom field values on multiple documents.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ids` | `array` | yes |  |
| `add_fields` | `array` | no |  |
| `remove_fields` | `array` | no |  |

## `bulk_modify_tags`

Add and/or remove tags on multiple documents atomically.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ids` | `array` | yes |  |
| `add_tags` | `array` | no |  |
| `remove_tags` | `array` | no |  |

## `bulk_remove_tag`

Remove a tag from multiple documents in a single request.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ids` | `array` | yes |  |
| `tag` | `integer` | yes |  |

## `bulk_set_correspondent`

Assign or clear a correspondent on multiple documents.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ids` | `array` | yes |  |
| `correspondent` | `integer` | yes |  |

## `bulk_set_correspondent_permissions`

Set permissions and/or owner on multiple correspondents.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ids` | `array` | yes |  |
| `set_permissions` | `object` | no |  |
| `owner` | `integer` | no |  |
| `merge` | `boolean` | no |  |

## `bulk_set_document_type`

Assign or clear a document type on multiple documents.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ids` | `array` | yes |  |
| `document_type` | `integer` | yes |  |

## `bulk_set_document_type_permissions`

Set permissions and/or owner on multiple document types.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ids` | `array` | yes |  |
| `set_permissions` | `object` | no |  |
| `owner` | `integer` | no |  |
| `merge` | `boolean` | no |  |

## `bulk_set_permissions`

Set permissions and/or owner on multiple documents.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ids` | `array` | yes |  |
| `set_permissions` | `object` | no |  |
| `owner` | `integer` | no |  |
| `merge` | `boolean` | no |  |

## `bulk_set_storage_path`

Assign or clear a storage path on multiple documents.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ids` | `array` | yes |  |
| `storage_path` | `integer` | yes |  |

## `bulk_set_storage_path_permissions`

Set permissions and/or owner on multiple storage paths.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ids` | `array` | yes |  |
| `set_permissions` | `object` | no |  |
| `owner` | `integer` | no |  |
| `merge` | `boolean` | no |  |

## `bulk_set_tag_permissions`

Set permissions and/or owner on multiple tags.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ids` | `array` | yes |  |
| `set_permissions` | `object` | no |  |
| `owner` | `integer` | no |  |
| `merge` | `boolean` | no |  |

## `create_correspondent`

Create a new correspondent.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | `string` | yes |  |
| `match` | `string` | no |  |
| `matching_algorithm` | `integer` | no |  |
| `is_insensitive` | `boolean` | no |  |
| `owner` | `integer` | no |  |
| `set_permissions` | `object` | no |  |

## `create_custom_field`

Create a new custom field.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | `string` | yes |  |
| `data_type` | `string` | yes |  |
| `extra_data` | `object` | no |  |
| `owner` | `integer` | no |  |
| `set_permissions` | `object` | no |  |

## `create_document_note`

Add a new note to a document.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document_id` | `integer` | yes |  |
| `note` | `string` | yes |  |

## `create_document_type`

Create a new document type.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | `string` | yes |  |
| `match` | `string` | no |  |
| `matching_algorithm` | `integer` | no |  |
| `is_insensitive` | `boolean` | no |  |
| `owner` | `integer` | no |  |
| `set_permissions` | `object` | no |  |

## `create_storage_path`

Create a new storage path.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | `string` | yes |  |
| `path` | `string` | yes |  |
| `match` | `string` | no |  |
| `matching_algorithm` | `integer` | no |  |
| `is_insensitive` | `boolean` | no |  |
| `owner` | `integer` | no |  |
| `set_permissions` | `object` | no |  |

## `create_tag`

Create a new tag.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | `string` | yes |  |
| `color` | `string` | no |  |
| `is_inbox_tag` | `boolean` | no |  |
| `match` | `string` | no |  |
| `matching_algorithm` | `integer` | no |  |
| `is_insensitive` | `boolean` | no |  |
| `parent` | `integer` | no |  |
| `owner` | `integer` | no |  |
| `set_permissions` | `object` | no |  |

## `create_user`

Create a new user account.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `username` | `string` | yes |  |
| `email` | `string` | no |  |
| `password` | `string` | no |  |
| `first_name` | `string` | no |  |
| `last_name` | `string` | no |  |
| `date_joined` | `string` | no |  |
| `is_staff` | `boolean` | no |  |
| `is_active` | `boolean` | no |  |
| `is_superuser` | `boolean` | no |  |
| `groups` | `array` | no |  |
| `user_permissions` | `array` | no |  |

## `delete_correspondent`

Permanently delete a correspondent by its ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `integer` | yes |  |

## `delete_custom_field`

Permanently delete a custom field by its ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `integer` | yes |  |

## `delete_document`

Permanently delete a document by its ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `integer` | yes |  |

## `delete_document_note`

Permanently delete a note from a document.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document_id` | `integer` | yes |  |
| `note_id` | `integer` | yes |  |

## `delete_document_type`

Permanently delete a document type by its ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `integer` | yes |  |

## `delete_storage_path`

Permanently delete a storage path by its ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `integer` | yes |  |

## `delete_tag`

Permanently delete a tag by its ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `integer` | yes |  |

## `delete_user`

Permanently delete a user account by their ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `integer` | yes |  |

## `empty_trash`

Permanently delete specific documents from the trash.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document_ids` | `array` | yes |  |

## `get_correspondent`

Fetch a single correspondent by its ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `integer` | yes |  |

## `get_custom_field`

Fetch a single custom field by its ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `integer` | yes |  |

## `get_document`

Retrieve a single document by its ID with configurable field selection.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `integer` | yes |  |
| `include_metadata` | `boolean` | no |  |
| `return_fields` | `array` | no |  |

## `get_document_metadata`

Retrieve file-level technical metadata for a document.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `integer` | yes |  |

## `get_document_type`

Fetch a single document type by its ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `integer` | yes |  |

## `get_storage_path`

Fetch a single storage path by its ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `integer` | yes |  |

## `get_tag`

Fetch a single tag by its ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `integer` | yes |  |

## `get_user`

Fetch a single user by their ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `integer` | yes |  |

## `list_correspondents`

List correspondents defined in paperless-ngx with optional filtering.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ids` | `array` | no |  |
| `name_contains` | `string` | no |  |
| `name_exact` | `string` | no |  |
| `page` | `integer` | no |  |
| `page_size` | `integer` | no |  |
| `ordering` | `string` | no |  |
| `descending` | `boolean` | no |  |

## `list_custom_fields`

List custom fields defined in paperless-ngx with optional filtering.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name_contains` | `string` | no |  |
| `name_exact` | `string` | no |  |
| `page` | `integer` | no |  |
| `page_size` | `integer` | no |  |
| `ordering` | `string` | no |  |
| `descending` | `boolean` | no |  |

## `list_document_notes`

List all notes attached to a document.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document_id` | `integer` | yes |  |
| `page` | `integer` | no |  |
| `page_size` | `integer` | no |  |

## `list_document_types`

List document types defined in paperless-ngx with optional filtering.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ids` | `array` | no |  |
| `name_contains` | `string` | no |  |
| `name_exact` | `string` | no |  |
| `page` | `integer` | no |  |
| `page_size` | `integer` | no |  |
| `ordering` | `string` | no |  |
| `descending` | `boolean` | no |  |

## `list_documents`

List documents from paperless-ngx with optional filtering.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `search` | `string` | no |  |
| `search_mode` | `string` | no |  |
| `ids` | `array` | no |  |
| `tags` | `array` | no |  |
| `any_tags` | `array` | no |  |
| `exclude_tags` | `array` | no |  |
| `correspondent` | `integer` | no |  |
| `any_correspondent` | `array` | no |  |
| `exclude_correspondents` | `array` | no |  |
| `document_type` | `integer` | no |  |
| `document_type_name_contains` | `string` | no |  |
| `document_type_name_exact` | `string` | no |  |
| `any_document_type` | `array` | no |  |
| `exclude_document_types` | `array` | no |  |
| `storage_path` | `integer` | no |  |
| `any_storage_paths` | `array` | no |  |
| `exclude_storage_paths` | `array` | no |  |
| `owner` | `integer` | no |  |
| `exclude_owners` | `array` | no |  |
| `custom_fields` | `array` | no |  |
| `any_custom_fields` | `array` | no |  |
| `exclude_custom_fields` | `array` | no |  |
| `custom_field_query` | `array` | no |  |
| `created_after` | `string` | no |  |
| `created_before` | `string` | no |  |
| `added_after` | `string` | no |  |
| `added_from` | `string` | no |  |
| `added_before` | `string` | no |  |
| `added_until` | `string` | no |  |
| `modified_after` | `string` | no |  |
| `modified_from` | `string` | no |  |
| `modified_before` | `string` | no |  |
| `modified_until` | `string` | no |  |
| `archive_serial_number` | `integer` | no |  |
| `archive_serial_number_from` | `integer` | no |  |
| `archive_serial_number_till` | `integer` | no |  |
| `checksum` | `string` | no |  |
| `ordering` | `string` | no |  |
| `page` | `integer` | no |  |
| `page_size` | `integer` | no |  |
| `descending` | `boolean` | no |  |
| `max_results` | `integer` | no |  |
| `return_fields` | `array` | no |  |

## `list_storage_paths`

List storage paths defined in paperless-ngx with optional filtering.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ids` | `array` | no |  |
| `name_contains` | `string` | no |  |
| `name_exact` | `string` | no |  |
| `path_contains` | `string` | no |  |
| `path_exact` | `string` | no |  |
| `page` | `integer` | no |  |
| `page_size` | `integer` | no |  |
| `ordering` | `string` | no |  |
| `descending` | `boolean` | no |  |

## `list_tags`

List tags defined in paperless-ngx with optional filtering.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ids` | `array` | no |  |
| `name_contains` | `string` | no |  |
| `name_exact` | `string` | no |  |
| `page` | `integer` | no |  |
| `page_size` | `integer` | no |  |
| `ordering` | `string` | no |  |
| `descending` | `boolean` | no |  |

## `list_trash`

List all documents currently in the paperless-ngx trash.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | `integer` | no |  |
| `page_size` | `integer` | no |  |

## `list_users`

List users defined in paperless-ngx with optional filtering.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `username_contains` | `string` | no |  |
| `username_exact` | `string` | no |  |
| `ordering` | `string` | no |  |
| `page` | `integer` | no |  |
| `page_size` | `integer` | no |  |

## `restore_trash`

Restore trashed documents back to active status.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document_ids` | `array` | yes |  |

## `update_correspondent`

Partially update a correspondent (PATCH semantics).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `integer` | yes |  |
| `name` | `string` | no |  |
| `match` | `string` | no |  |
| `matching_algorithm` | `integer` | no |  |
| `is_insensitive` | `boolean` | no |  |
| `owner` | `integer` | no |  |
| `set_permissions` | `object` | no |  |

## `update_custom_field`

Partially update a custom field (PATCH semantics).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `integer` | yes |  |
| `name` | `string` | no |  |
| `data_type` | `string` | no |  |
| `extra_data` | `object` | no |  |
| `owner` | `integer` | no |  |
| `set_permissions` | `object` | no |  |

## `update_document`

Partially update a document (PATCH semantics).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `integer` | yes |  |
| `title` | `string` | no |  |
| `content` | `string` | no |  |
| `created` | `string` | no |  |
| `correspondent` | `integer` | no |  |
| `document_type` | `integer` | no |  |
| `storage_path` | `integer` | no |  |
| `tags` | `array` | no |  |
| `archive_serial_number` | `integer` | no |  |
| `custom_fields` | `array` | no |  |
| `owner` | `integer` | no |  |
| `set_permissions` | `object` | no |  |
| `remove_inbox_tags` | `boolean` | no |  |

## `update_document_type`

Partially update a document type (PATCH semantics).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `integer` | yes |  |
| `name` | `string` | no |  |
| `match` | `string` | no |  |
| `matching_algorithm` | `integer` | no |  |
| `is_insensitive` | `boolean` | no |  |
| `owner` | `integer` | no |  |
| `set_permissions` | `object` | no |  |

## `update_storage_path`

Partially update a storage path (PATCH semantics).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `integer` | yes |  |
| `name` | `string` | no |  |
| `path` | `string` | no |  |
| `match` | `string` | no |  |
| `matching_algorithm` | `integer` | no |  |
| `is_insensitive` | `boolean` | no |  |
| `owner` | `integer` | no |  |
| `set_permissions` | `object` | no |  |

## `update_tag`

Partially update a tag (PATCH semantics).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `integer` | yes |  |
| `name` | `string` | no |  |
| `color` | `string` | no |  |
| `is_inbox_tag` | `boolean` | no |  |
| `match` | `string` | no |  |
| `matching_algorithm` | `integer` | no |  |
| `is_insensitive` | `boolean` | no |  |
| `parent` | `integer` | no |  |
| `owner` | `integer` | no |  |
| `set_permissions` | `object` | no |  |

## `update_user`

Partially update a user account (PATCH semantics).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `integer` | yes |  |
| `username` | `string` | no |  |
| `email` | `string` | no |  |
| `password` | `string` | no |  |
| `first_name` | `string` | no |  |
| `last_name` | `string` | no |  |
| `date_joined` | `string` | no |  |
| `is_staff` | `boolean` | no |  |
| `is_active` | `boolean` | no |  |
| `is_superuser` | `boolean` | no |  |
| `groups` | `array` | no |  |
| `user_permissions` | `array` | no |  |

## `upload_document`

Upload a document file to paperless-ngx.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | `string` | yes |  |
| `title` | `string` | no |  |
| `created` | `string` | no |  |
| `correspondent` | `integer` | no |  |
| `document_type` | `integer` | no |  |
| `storage_path` | `integer` | no |  |
| `tags` | `array` | no |  |
| `archive_serial_number` | `integer` | no |  |
| `custom_fields` | `array` | no |  |
| `wait` | `boolean` | no |  |

