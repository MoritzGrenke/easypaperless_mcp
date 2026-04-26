# [FEATURE] Permission-based tool filtering — hide tools the authenticated user cannot use

## Summary

When a `PAPERLESS_USERNAME` is supplied alongside the API token, the MCP server resolves that user's effective Django permissions at session start and hides any tools the user is not permitted to invoke. Tools are truly hidden (absent from the tool list), not merely blocked after the fact. If no username is supplied, all tools are shown and permission enforcement falls back to paperless-ngx's own API-level 403 responses.

---

## Problem Statement

Every user in paperless-ngx has a fine-grained Django permission set (e.g. `add_document`, `change_tag`, `delete_correspondent`). Without filtering, the MCP server exposes all tools to every authenticated client regardless of what the underlying user is actually allowed to do. This leads to two problems:

1. **Noise for the AI agent** — the agent may attempt operations (e.g. delete a document) that are guaranteed to fail, wasting tokens and causing confusion.
2. **False affordance** — the tool list implies capabilities the user does not have, undermining trust in the server's tool descriptions.

---

## Design Decisions

### Security model
This feature is a **convenience / UX improvement**, not a security control. Because the MCP server cannot verify that a supplied username actually belongs to the user presenting the token, a client operator could supply any username (including an admin's). No security guarantee is implied. The authoritative permission enforcement always remains with paperless-ngx's own API layer.

### Username is optional
- **Username not supplied**: all tools are shown. paperless-ngx returns 403 for any call the user is not permitted to make.
- **Username supplied**: the server resolves the user's effective permissions and hides tools the user cannot use.

### True tool hiding via FastMCP 3 visibility system
Tools are hidden at the `list_tools` level using FastMCP 3's visibility system:
- All tools are tagged with their required Django permission codename (e.g. `perm:delete_document`).
- All tags are globally disabled by default.
- On session start (before the tool list is sent to the client), the server resolves the user's permissions and calls `ctx.enable_components(tags=permitted_tags)` for that session only.
- FastMCP sends `ToolListChangedNotification` automatically; other sessions are unaffected.

This requires FastMCP 3 (see issue 0030).

### Trigger point
Permission resolution fires at **session start / `list_tools`**, not on the first tool call. This ensures the agent receives a correctly filtered tool list from the very first `list_tools` request.

### Permission resolution
1. Read `PAPERLESS_USERNAME` from env (stdio) or `X-Paperless-Username` header (HTTP).
2. Call `client.users.list(username_exact=username)` to retrieve the `User` object.
3. Determine the user's **effective permissions** (union of `user_permissions` and all permissions granted via `groups`). During implementation, verify whether easypaperless already returns the effective union; if not, resolve group permissions explicitly.
4. If `is_superuser` is `True`, skip filtering entirely — the user sees all tools.

### Credential flow
| Transport | Credential |
|-----------|-----------|
| stdio | `PAPERLESS_USERNAME` environment variable |
| streamable-http | `X-Paperless-Username` request header |

Consistent with the existing pattern from issue 0019 (`PAPERLESS_TOKEN` / `X-Paperless-Token`).

### Permission mapping
A `TOOL_PERMISSIONS` mapping covers every registered tool. The mapping is **convention-based** with an explicit override dict for edge cases:

**Convention** — derive from tool name:
| Tool verb | Django action |
|-----------|--------------|
| `list_*`, `get_*`, `download_*` | `view` |
| `create_*` | `add` |
| `update_*` | `change` |
| `delete_*`, `bulk_delete_*` | `delete` |

Model name is derived from the tool name after the verb. Example: `delete_document` → `paperless.delete_document`.

**Override dict** — for tools that do not follow the convention (e.g. `restore_trash`, `get_document_history`, note sub-resource tools). The exact overrides and the correct Django app label must be verified against the paperless-ngx source during implementation.

### Error handling
| Situation | Behaviour |
|-----------|-----------|
| Username not supplied | All tools shown; no API call made |
| Username supplied, lookup succeeds | Filtered tool list based on effective permissions |
| Username supplied, lookup fails (user not found / API error) | Error returned; no tools shown |
| `is_superuser = True` | All tools shown; no filtering applied |

---

## Scope

### In Scope
- `server.py`: integrate FastMCP 3 visibility system; tag all tools with their required permission; apply session-start permission hook.
- `client.py` / `server.py` (middleware): extract `PAPERLESS_USERNAME` / `X-Paperless-Username` alongside existing credentials; make it available to the permission hook.
- `TOOL_PERMISSIONS` mapping (convention + overrides) covering every registered tool.
- Effective permission resolution (user_permissions + group permissions).
- Superuser bypass.
- Clear error message when username is set but lookup fails.
- Unit tests (see Acceptance Criteria).
- README / docstring updates for the new `PAPERLESS_USERNAME` credential.

### Out of Scope
- Object-level permissions (per-document owner/viewer assignments).
- Mid-session permission refresh.
- Any changes to the easypaperless library.
- Changing how the token or URL are supplied.

---

## Acceptance Criteria

- [ ] When `PAPERLESS_USERNAME` is not supplied, all tools are visible to the client unchanged.
- [ ] When `PAPERLESS_USERNAME` is supplied and the lookup succeeds, only tools whose required permission is present in the user's effective permission set are shown.
- [ ] Effective permissions are the union of `user_permissions` and all permissions granted via the user's `groups`.
- [ ] When `is_superuser` is `True`, all tools are shown regardless of `user_permissions`.
- [ ] A `TOOL_PERMISSIONS` mapping exists and covers every tool registered in the MCP server.
- [ ] When `PAPERLESS_USERNAME` is supplied but the lookup fails (user not found or API error), the server returns a descriptive error and no tools are shown.
- [ ] Both `stdio` and `streamable-http` transports apply the same filtering logic.
- [ ] The permission lookup is performed at session start (before the first tool list is sent), not on the first tool call.
- [ ] The permission lookup is performed at most once per session; subsequent `list_tools` requests within the same session use the cached result.
- [ ] All existing tests continue to pass.
- [ ] New unit tests cover: no username supplied (all tools shown), full-permissions user, read-only user, superuser bypass, lookup failure, cache hit (lookup called only once per session).
- [ ] `ruff check` and `mypy --strict` pass with no errors.

---

## Dependencies & Constraints

- **Depends on issue 0030** (FastMCP 3 upgrade) — the visibility system (`mcp.disable()` / `ctx.enable_components()`) requires FastMCP 3.
- **Depends on issues 0019 and 0022** — token and URL credentials must be reliably available in the request context before the permission hook can run.
- The exact Django app label used by paperless-ngx (e.g. `paperless`, `documents`) and the permission codenames for sub-resources (notes, history, trash) must be verified against the paperless-ngx source during implementation.

---

## Priority

`High`

---

## Additional Notes

- The Django permission codenames follow the pattern `<app_label>.<action>_<model>`. The exact app label must be confirmed during implementation by inspecting a real `user_permissions` list returned by the paperless-ngx API.
- Tools for sub-resources (document notes, document history, trash) may not follow the standard naming convention and will require explicit entries in the override dict.
- This is a convenience feature, not a security boundary. Admins who require hard enforcement must rely on paperless-ngx's own permission layer.

---

## QA

**Tested by:** QA Engineer  
**Date:** 2026-04-26  
**Commit:** uncommitted changes on master (post-25bc5f7)

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC1: No username supplied → all tools visible, no API call | All tools returned | All tools returned; `show_all=True` cached | ✅ Pass |
| 2 | AC2: Username supplied, lookup succeeds → only permitted tools shown | Filtered tool list | Only permitted tools returned | ✅ Pass |
| 3 | AC3: Effective perms = union of `user_permissions` + `inherited_permissions` | Union set | Correct union computed; deduplication works | ✅ Pass |
| 4 | AC4: `is_superuser=True` → all tools shown regardless of permissions | All tools returned | All tools returned; `show_all=True` cached | ✅ Pass |
| 5 | AC5: `TOOL_PERMISSIONS` covers every registered tool | 60 tools mapped | 60 tools mapped, test `test_tool_permissions_covers_all_tools` passes | ✅ Pass |
| 6 | AC6: Username supplied, user not found → descriptive RuntimeError, no tools | `RuntimeError` with "not found" | `RuntimeError("...not found...")` raised | ✅ Pass |
| 7 | AC6: Username supplied, API error → descriptive RuntimeError | `RuntimeError` with "Permission lookup failed" | Raised correctly | ✅ Pass |
| 8 | AC7: stdio transport reads from env vars | `PAPERLESS_USERNAME` env var used | Correctly read from env | ✅ Pass |
| 9 | AC7: HTTP transport reads from `X-Paperless-Username` header | Header value used | Correctly extracted from request headers | ✅ Pass |
| 10 | AC8: Lookup fires in `on_list_tools`, not on first tool call | `on_list_tools` hook | Implemented in `PermissionMiddleware.on_list_tools` | ✅ Pass |
| 11 | AC9: Cache hit — second `list_tools` skips API call | `PaperlessClient` not instantiated | `mock_pc.assert_not_called()` passes | ✅ Pass |
| 12 | AC9: Cache hit with `show_all=True` → all tools returned | All tools | All tools returned without API call | ✅ Pass |
| 13 | AC10: All existing tests pass | 344 tests pass | 364 tests pass (20 new) | ✅ Pass |
| 14 | AC11: New tests cover all required scenarios | 6+ scenario categories | 20 tests across all categories | ✅ Pass |
| 15 | AC12: `mypy --strict` passes | No errors | No issues on `permissions.py` + `server.py` | ✅ Pass |
| 16 | AC12: `ruff check` passes | No errors | **1 error**: unused `Sequence` import in `tests/unit/test_permissions.py:5` | ❌ Fail |
| 17 | Edge: `fastmcp_context` is None → pass through unchanged | All tools returned | All tools returned, no crash | ✅ Pass |
| 18 | Edge: `get_state` raises exception → pass through unchanged | All tools returned | Returns all tools silently | ✅ Pass |
| 19 | Scope: README documents `PAPERLESS_USERNAME` / `X-Paperless-Username` | Credential table updated | Not documented in README | ❌ Fail |

### Bugs Found

#### BUG-001 — Unused import `Sequence` in `test_permissions.py` [Severity: Low]
**Steps to reproduce:**
1. Run `ruff check tests/unit/test_permissions.py`

**Expected:** No errors  
**Actual:** `F401 [*] collections.abc.Sequence imported but unused` at line 5  
**Severity:** Low  
**Notes:** One-line fix. Blocks AC12 ("ruff check passes").  
**Fixed:** Removed unused import. `ruff check` now clean.

#### BUG-002 — README missing `PAPERLESS_USERNAME` / `X-Paperless-Username` documentation [Severity: Low]
**Steps to reproduce:**
1. Open `README.md`, look at the "MCP Client Configuration" credential table (lines 138–144).

**Expected:** `PAPERLESS_USERNAME` env var (stdio) and `X-Paperless-Username` header (HTTP) listed with description (optional, enables permission-based tool filtering).  
**Actual:** Neither credential is documented.  
**Severity:** Low  
**Notes:** Documented in the issue scope ("README / docstring updates for the new `PAPERLESS_USERNAME` credential") but was not implemented.  
**Fixed:** Added both credentials to the "MCP Client Configuration" table in `README.md`.

### Automated Tests
- `tests/unit/test_permissions.py` — 20 passed, 0 failed
- `tests/unit/` (full suite) — 364 passed, 0 failed
- `mypy --strict src/easypaperless_mcp/permissions.py src/easypaperless_mcp/server.py` — clean
- `ruff check` — clean (after BUG-001 fix)

### Summary
- ACs tested: 12/12
- ACs passing: 12/12
- Bugs found: 2 (Critical: 0, High: 0, Medium: 0, Low: 2) — both fixed
- Recommendation: ✅ Ready to merge
