# [BUG] Documents tools have incomplete easypaperless API coverage

## Summary

Several tools in `tools/documents.py` are missing parameters that exist in the underlying easypaperless `SyncDocumentsResource`, and the document notes sub-resource (`client.documents.notes`) is not exposed at all. This means agents cannot access full document capabilities through the MCP server.

---

## Environment

- **Version / Release:** current `master`
- **Other relevant context:** Reference: `dev/easypaperless_v0.2.0_sync_methods_overview.md`

---

## Steps to Reproduce

1. Open `src/easypaperless_mcp/tools/documents.py`.
2. Compare each tool's parameters against the corresponding method in the sync methods overview.
3. Observe the gaps listed below.

---

## Expected Behavior

Every parameter exposed by `SyncDocumentsResource` in easypaperless v0.2.0 is reachable via a corresponding MCP tool parameter. The notes sub-resource (`client.documents.notes`) is fully exposed with `list`, `create`, and `delete` tools.

---

## Actual Behavior

The following parameters and tools are missing:

### `get_document` — missing parameters

| easypaperless param | Type | Default | Notes |
|---|---|---|---|
| `include_metadata` | `bool` | `False` | Fetches extended file-level metadata and attaches it to the document |

### `update_document` — missing parameters

| easypaperless param | Type | Default | Notes |
|---|---|---|---|
| `custom_fields` | `list[dict[str, Any]] \| None \| UNSET` | `UNSET` | List of `{"field": <id>, "value": ...}` dicts |
| `owner` | `int \| None \| UNSET` | `UNSET` | Numeric user ID; `None` clears; UNSET leaves unchanged |
| `set_permissions` | `SetPermissions \| None \| UNSET` | `UNSET` | Explicit view/change permission sets |

> Note: `owner` and `set_permissions` follow the same `clear_*` flag or UNSET sentinel pattern already used for other nullable fields in the tool.

### `upload_document` — missing parameters

| easypaperless param | Type | Default | Notes |
|---|---|---|---|
| `custom_fields` | `list[dict[str, Any]] \| None` | `None` | List of `{"field": <id>, "value": ...}` dicts |

### `list_documents` — missing parameters

The tool exposes `added_after` / `added_before` and `modified_after` / `modified_before` but is missing the four inclusive-boundary variants:

| easypaperless param | Type | Default | Notes |
|---|---|---|---|
| `added_from` | `date \| datetime \| str \| None` | `None` | Documents added **on or after** this datetime (inclusive) |
| `added_until` | `date \| datetime \| str \| None` | `None` | Documents added **on or before** this datetime (inclusive) |
| `modified_from` | `date \| datetime \| str \| None` | `None` | Documents modified **on or after** this datetime (inclusive) |
| `modified_until` | `date \| datetime \| str \| None` | `None` | Documents modified **on or before** this datetime (inclusive) |

---

## Impact

- **Severity:** `Medium`
- **Affected Users / Systems:** Any AI agent using the MCP server that needs to set custom fields, manage permissions, attach document metadata, or filter by inclusive date bounds.

---

## Acceptance Criteria

- [ ] `get_document` accepts and forwards `include_metadata: bool = False` to `client.documents.get`.
- [ ] `update_document` accepts `custom_fields`, `owner` / `clear_owner`, and `set_permissions` and forwards them correctly using the UNSET sentinel pattern.
- [ ] `upload_document` accepts `custom_fields` and forwards it to `client.documents.upload`.
- [ ] `list_documents` accepts `added_from`, `added_until`, `modified_from`, and `modified_until` and forwards them to `client.documents.list`.
- [ ] All new parameters are covered by unit tests.
- [ ] No existing tests are broken.

---

## Additional Notes

- The `clear_owner` pattern (boolean flag to send `None` to the API) should be consistent with `clear_correspondent`, `clear_document_type`, etc. already in `update_document`.

---

## QA

**Tested by:** QA Engineer
**Date:** 2026-03-15
**Commit:** 7fac5e6 (uncommitted changes on top)

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC1: `get_document` accepts `include_metadata: bool = False` | Parameter present, forwarded to `client.documents.get` | Parameter declared at signature, forwarded as `client.documents.get(id=..., include_metadata=include_metadata)` | ✅ Pass |
| 2 | AC1 edge: `include_metadata=True` forwarded correctly | `True` passed to client | `client.documents.get(id=1, include_metadata=True)` confirmed via unit test | ✅ Pass |
| 3 | AC2: `update_document` accepts `custom_fields` and forwards it | `custom_fields` in kwargs when provided, absent when None | Correct — if-not-None guard; not sent when None | ✅ Pass |
| 4 | AC2: `update_document` accepts `owner` and forwards it | `owner` in kwargs when provided | Correct — sent as integer | ✅ Pass |
| 5 | AC2: `clear_owner=True` sends `owner=None` to API | `kwargs["owner"] is None` | Correct — clear_owner takes precedence over owner value | ✅ Pass |
| 6 | AC2: `clear_owner=True` + `owner=5` — clear wins | `kwargs["owner"] is None` | Confirmed by `test_update_document_clear_owner_takes_precedence` | ✅ Pass |
| 7 | AC2: `set_permissions` forwarded when provided | `set_permissions` in kwargs | Correct — forwarded via if-not-None guard | ✅ Pass |
| 8 | AC2: `owner` and `set_permissions` absent when not provided | Neither key in kwargs | Confirmed by omit tests | ✅ Pass |
| 9 | AC3: `upload_document` accepts `custom_fields` and forwards it | `custom_fields` in kwargs when provided, absent when None | Correct — if-not-None guard consistent with other params | ✅ Pass |
| 10 | AC4: `list_documents` accepts `added_from` / `added_until` | Both forwarded to `client.documents.list` | Correct — forwarded via if-not-None guards | ✅ Pass |
| 11 | AC4: `list_documents` accepts `modified_from` / `modified_until` | Both forwarded to `client.documents.list` | Correct — forwarded via if-not-None guards | ✅ Pass |
| 12 | AC4 edge: inclusive date bounds absent when None | Keys not in call kwargs | Confirmed by `test_list_documents_omits_inclusive_date_bounds_when_none` | ✅ Pass |
| 13 | AC5: All new parameters covered by unit tests | ≥1 test per new parameter | 17 new unit tests added covering all new params and notes tools | ✅ Pass |
| 14 | AC6: No existing tests broken | Full unit suite passes | 75/75 tests pass | ✅ Pass |
| 15 | Bonus: Notes sub-resource exposed (`list_document_notes`, `create_document_note`, `delete_document_note`) | Mentioned in Expected Behavior but not in ACs | All 3 tools implemented and tested — exceeds AC scope | ✅ Pass |
| 16 | Regression: Existing `update_document` clear_* flags still work | `clear_correspondent`, `clear_document_type`, etc. unaffected | All pre-existing clear_* tests pass | ✅ Pass |
| 17 | Static analysis: ruff lint | No lint errors | All checks passed | ✅ Pass |
| 18 | Static analysis: mypy type checking | No new type errors | 2 pre-existing errors (`easypaperless` missing stubs) — same before and after changes; not introduced by this issue | ✅ Pass |

### Bugs Found

None.

### Automated Tests

- Suite: `tests/unit/` — 75 passed, 0 failed
- New tests for this issue: 17 (lines 548–691 in `test_documents.py`)

### Summary

- ACs tested: 6/6
- ACs passing: 6/6
- Bugs found: 0 (Critical: 0, High: 0, Medium: 0, Low: 0)
- Recommendation: ✅ Ready to merge
