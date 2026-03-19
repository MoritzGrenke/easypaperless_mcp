# [BUG] Document notes tools registered twice, causing duplicate tool names

## Summary

The three document notes tools (`list_document_notes`, `create_document_note`, `delete_document_note`) are defined in both `tools/documents.py` and `tools/document_notes.py`. Because both sub-servers are mounted without a namespace in `server.py`, all three tool names are registered twice in the MCP server. An AI client that introspects the tool list will see duplicates, which is undefined behavior and may cause tool-call failures or ambiguity.

---

## Steps to Reproduce

1. Run `python scripts/inspect_tools.py` (or any MCP introspection).
2. Observe that `create_document_note`, `delete_document_note`, and `list_document_notes` each appear twice with different parameter names (`id` vs. `document_id`).

---

## Expected Behavior

Each tool name appears exactly once in the MCP tool registry, registered under the dedicated `document_notes` sub-server.

---

## Actual Behavior

Each of the three tools appears twice:
- Once from `tools/documents.py` (parameter name: `id`)
- Once from `tools/document_notes.py` (parameter name: `document_id`)

---

## Root Cause

When issue 0011 added the dedicated `document_notes` sub-server, the notes tool definitions in `tools/documents.py` were not removed. Both registrations survive into the mounted MCP server.

---

## Impact

- **Severity:** `High`
- **Affected Users / Systems:** All MCP clients — the duplicate names are visible to any AI agent that lists tools.

---

## Acceptance Criteria

- [ ] The three notes tools (`list_document_notes`, `create_document_note`, `delete_document_note`) are no longer defined in `tools/documents.py`.
- [ ] The tools remain fully functional via the `document_notes` sub-server in `tools/document_notes.py`.
- [ ] Running the introspection script shows each tool name exactly once.
- [ ] All existing tests for document notes pass without modification.
- [ ] No other tools are accidentally removed from `tools/documents.py`.

---

## Out of Scope

- Changing the parameter names or behavior of the remaining tool definitions in `document_notes.py`.
- Any other refactoring of `documents.py`.

---

## Additional Notes

- Related: issue 0011 (document notes sub-server feature).
- The correct canonical definitions are in `tools/document_notes.py`; those use `document_id` as the parameter name, which is consistent with the `document_notes` sub-server's own convention. The `id`-named variants in `documents.py` should be deleted.

---

## QA

**Tested by:** QA Engineer
**Date:** 2026-03-19
**Commit:** 2ed3279 (working tree, uncommitted changes)

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC1: Notes tools absent from `tools/documents.py` | No definitions of `list_document_notes`, `create_document_note`, `delete_document_note` in documents.py | `grep` returns no matches — all three removed | ✅ Pass |
| 2 | AC2: Notes tools present and functional in `tools/document_notes.py` | All three tools defined with `document_id` param | All three found at lines 13, 35, 50 | ✅ Pass |
| 3 | AC3: Introspection shows each tool name exactly once | `uniq -d` on tool list returns empty (no duplicates); each of the 3 tools appears exactly once | 51 total tools, no duplicate names found, each notes tool appears exactly once with `document_id` param | ✅ Pass |
| 4 | AC4: All document notes unit tests pass | 12 tests in `test_document_notes.py` all pass | 12/12 passed | ✅ Pass |
| 5 | AC5: No other tools accidentally removed from `documents.py` | All non-notes document tools still present | `bulk_*`, `list_documents`, `get_document`, `update_document`, `delete_document`, `upload_document`, `get_document_metadata` all present and tested (78 tests pass) | ✅ Pass |
| 6 | Edge: `DocumentNote` import removed from `documents.py` | Import no longer needed after removal | Import correctly removed, no `NameError` | ✅ Pass |
| 7 | Integration: Notes tools functional against live paperless-ngx | list/create/delete notes work end-to-end | 5 integration tests all pass (list, count, pagination, create+delete round-trip) | ✅ Pass |

### Bugs Found

None.

### Automated Tests

- Unit suite (`tests/unit/`) — 232 passed, 0 failed
- Integration suite (`tests/integration/` — notes only) — 5 passed, 0 failed

### Summary

- ACs tested: 5/5
- ACs passing: 5/5
- Bugs found: 0
- Recommendation: ✅ Ready to merge
