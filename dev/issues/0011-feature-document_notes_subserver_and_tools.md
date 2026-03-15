# [FEATURE] Document notes sub-server with full resource tool coverage

## Summary

Expose the `client.documents.notes` sub-resource of easypaperless as a dedicated FastMCP sub-server, implementing all three available operations as MCP tools. This enables AI agents to read, add, and remove notes on paperless-ngx documents.

---

## Problem Statement

The `documents.notes` sub-resource (`SyncNotesResource`) is not yet exposed through the MCP server. AI agents currently have no way to interact with document notes, which are important for collaborative annotation and document context.

---

## Proposed Solution

Create a new sub-server module `tools/document_notes.py` that wraps the three `client.documents.notes` methods as MCP tools and mounts it into the main server in `server.py`. The module follows the same conventions as existing sub-servers (e.g. `documents.py`, `tags.py`).

---

## User Stories

- As an AI agent, I want to list all notes on a document so that I can read annotations left by users.
- As an AI agent, I want to create a note on a document so that I can annotate it with observations or actions taken.
- As an AI agent, I want to delete a note from a document so that I can remove outdated or incorrect annotations.

---

## Scope

### In Scope
- `list_document_notes(document_id)` — wraps `client.documents.notes.list(document_id)`, returns `List[DocumentNote]`
- `create_document_note(document_id, note)` — wraps `client.documents.notes.create(document_id, note=note)`, returns `DocumentNote`
- `delete_document_note(document_id, note_id)` — wraps `client.documents.notes.delete(document_id, note_id)`, returns `None`
- New file `src/easypaperless_mcp/tools/document_notes.py` with its own `FastMCP` instance
- Sub-server mounted (without namespace) in `server.py`

### Out of Scope
- Modifying or updating existing notes (not supported by easypaperless)
- Bulk operations on notes (not supported by easypaperless)

---

## Acceptance Criteria

- [ ] `list_document_notes` tool exists, accepts `document_id: int`, and returns `List[DocumentNote]`
- [ ] `create_document_note` tool exists, accepts `document_id: int` and `note: str`, and returns `DocumentNote`
- [ ] `delete_document_note` tool exists, accepts `document_id: int` and `note_id: int`, and returns `None`
- [ ] All parameter names match the easypaperless API exactly (`document_id`, `note`, `note_id`)
- [ ] The sub-server is mounted in `server.py` without namespace
- [ ] The module is a standalone file `tools/document_notes.py` with its own `FastMCP` instance
- [ ] All tools have clear docstrings describing their purpose and parameters
- [ ] No existing tool or sub-server is modified beyond adding the mount in `server.py`

---

## Dependencies & Constraints

- Depends on `easypaperless>=0.2.0` providing `SyncNotesResource` at `client.documents.notes`
- Return type `DocumentNote` must be imported from easypaperless and returned directly (FastMCP serializes it)
- Follows the sub-server convention: `Resources and sub-resources separated` — notes live in `document_notes.py`, not in `documents.py`

---

## Priority

`Medium`

---

## Additional Notes

easypaperless API reference: `client.documents.notes` — `SyncNotesResource`

| Method | Parameters | Returns |
|--------|-----------|---------|
| `list(document_id)` | `document_id: int` | `List[DocumentNote]` |
| `create(document_id, *, note)` | `document_id: int`, `note: str` | `DocumentNote` |
| `delete(document_id, note_id)` | `document_id: int`, `note_id: int` | `None` |

---

## QA

**Tested by:** QA Engineer
**Date:** 2026-03-15
**Commit:** 649f3bc (HEAD — uncommitted changes present)

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC: `list_document_notes` exists, accepts `document_id: int`, returns `List[DocumentNote]` | Tool callable, correct signature, correct return type | Passes unit + integration | ✅ Pass |
| 2 | AC: `create_document_note` exists, accepts `document_id: int` and `note: str`, returns `DocumentNote` | Tool callable, `note` passed as kwarg, correct return type | Passes unit + integration | ✅ Pass |
| 3 | AC: `delete_document_note` exists, accepts `document_id: int` and `note_id: int`, returns `None` | Tool callable, both IDs forwarded as positional args | Passes unit + integration | ✅ Pass |
| 4 | AC: Parameter names match easypaperless API exactly (`document_id`, `note`, `note_id`) | Param names as specified | All names match | ✅ Pass |
| 5 | AC: Sub-server mounted in `server.py` without namespace | `document_notes` imported and mounted via `mcp.mount(document_notes)` | Confirmed in `server.py` lines 7, 15 | ✅ Pass |
| 6 | AC: Module is `tools/document_notes.py` with its own `FastMCP` instance | File exists, `document_notes = FastMCP("document_notes")` defined | Confirmed | ✅ Pass |
| 7 | AC: All tools have clear docstrings | Docstrings present for all 3 tools | All docstrings present and descriptive | ✅ Pass |
| 8 | AC: No existing tool or sub-server modified beyond mount in `server.py` | Only mount line added to server.py | Only import + mount added | ✅ Pass |
| 9 | Integration: create+delete round-trip cleans up | Created note appears in list, deleted note disappears | Round-trip passes live | ✅ Pass |
| 10 | Edge: list on document with no notes returns empty list | `[]` returned | Covered in unit test | ✅ Pass |

### Bugs Found

None.

### Automated Tests

- Unit suite (`tests/unit/test_document_notes.py`): **11 passed, 0 failed**
- Integration suite (`tests/integration/test_document_notes.py`): **3 passed, 0 failed**
- mypy (`--strict`): **0 errors** (document_notes.py is clean)
- ruff check: **0 violations**
- ruff format: **already formatted**

### Summary

- ACs tested: 8/8
- ACs passing: 8/8
- Bugs found: 0
- Recommendation: ✅ Ready to merge
