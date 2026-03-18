# Feature Index

**Next Available ID:** 0018

| ID | Type | Name | Status | File |
|----|------|------|--------|------|
| 0001 | feature | Documents sub-server with full resource tool coverage | QA PASSED | [0001-feature-documents_subserver_and_tools.md](0001-feature-documents_subserver_and_tools.md) |
| 0002 | feature | Full parameter coverage for list_documents tool | QA PASSED | [0002-feature-list_documents_full_parameter_coverage.md](0002-feature-list_documents_full_parameter_coverage.md) |
| 0003 | bug | `return_fields` filtering sets non-nullable fields to None, breaking output validation | QA PASSED | [0003-bug-filter_fields_none_breaks_validation.md](0003-bug-filter_fields_none_breaks_validation.md) |
| 0004 | bug | Documents tools have incomplete easypaperless API coverage | QA PASSED | [0004-bug-documents_tools_incomplete_api_coverage.md](0004-bug-documents_tools_incomplete_api_coverage.md) |
| 0005 | feature | Tags sub-server with full resource tool coverage | QA PASSED | [0005-feature-tags_subserver_and_tools.md](0005-feature-tags_subserver_and_tools.md) |
| 0006 | refactoring | Remove `clear_*` params from `update_document`, use `None` to clear nullable fields | QA PASSED | [0006-refactoring-remove_clear_params_from_update_document.md](0006-refactoring-remove_clear_params_from_update_document.md) |
| 0007 | refactoring | Rename `document_id`/`document_ids` params to `id`/`ids` in documents tools | QA PASSED | [0007-refactoring-rename_document_id_params_to_id.md](0007-refactoring-rename_document_id_params_to_id.md) |
| 0008 | feature | Correspondents sub-server with full resource tool coverage | QA PASSED | [0008-feature-correspondents_subserver_and_tools.md](0008-feature-correspondents_subserver_and_tools.md) |
| 0009 | feature | Custom fields sub-server with full resource tool coverage | QA PASSED | [0009-feature-custom_fields_subserver_and_tools.md](0009-feature-custom_fields_subserver_and_tools.md) |
| 0010 | feature | Document types sub-server with full resource tool coverage | QA PASSED | [0010-feature-document_types_subserver_and_tools.md](0010-feature-document_types_subserver_and_tools.md) |
| 0011 | feature | Document notes sub-server with full resource tool coverage | QA PASSED | [0011-feature-document_notes_subserver_and_tools.md](0011-feature-document_notes_subserver_and_tools.md) |
| 0012 | feature | Storage paths sub-server with full resource tool coverage | QA PASSED | [0012-feature-storage_paths_subserver_and_tools.md](0012-feature-storage_paths_subserver_and_tools.md) |
| 0013 | maintenance | Migrate easypaperless_mcp to easypaperless 0.3.0 | QA PASSED | [0013-maintenance-migrate_to_easypaperless_0_3_0.md](0013-maintenance-migrate_to_easypaperless_0_3_0.md) |
| 0014 | feature | Expose total count in list tool responses | QA PASSED | [0014-feature-list_tools_return_total_count.md](0014-feature-list_tools_return_total_count.md) |
| 0015 | bug | `list_correspondents` fails with plain HTTP request on HTTPS instances | RESOLVED | [0015-bug-https_url_sends_plain_http.md](0015-bug-https_url_sends_plain_http.md) |
| 0016 | maintenance | Migrate easypaperless_mcp to easypaperless 0.3.1 | OPEN | [0016-maintenance-migrate_to_easypaperless_0_3_1.md](0016-maintenance-migrate_to_easypaperless_0_3_1.md) |
| 0017 | bug | `_filter_fields` sets required non-nullable fields to `None` when omitted from `return_fields` | QA PASSED | [0017-bug-filter_fields_fails_for_required_fields.md](0017-bug-filter_fields_fails_for_required_fields.md) |