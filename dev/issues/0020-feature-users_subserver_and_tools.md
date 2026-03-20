# [FEATURE] Users sub-server with full resource tool coverage

## Summary

Add a `users` sub-server to easypaperless-mcp that exposes the `UsersResource` from easypaperless 0.4.0, giving AI agents full CRUD access to paperless-ngx user accounts.

---

## Problem Statement

easypaperless 0.4.0 introduced a `UsersResource` for managing paperless-ngx user accounts. This resource is not yet exposed as MCP tools, so AI agents cannot list, inspect, create, update, or delete users.

---

## Proposed Solution

Create `src/easypaperless_mcp/tools/users.py` as a new FastMCP sub-server following the same conventions as the existing resource sub-servers (tags, correspondents, etc.). Mount it in `server.py`. Expose all five operations available in `SyncUsersResource`.

---

## User Stories

- As an AI agent, I want to list all users so that I can audit who has access to the paperless-ngx instance.
- As an AI agent, I want to get a single user by ID so that I can inspect their roles and permissions.
- As an AI agent, I want to create a user so that I can help set up a new paperless-ngx instance.
- As an AI agent, I want to update a user so that I can change their roles, permissions, or activation status.
- As an AI agent, I want to delete a user so that I can remove accounts that are no longer needed.

---

## Scope

### In Scope
- `list_users` tool — wraps `SyncUsersResource.list()`, returns `ListResult[User]` (count + results)
- `get_user` tool — wraps `SyncUsersResource.get(id)`
- `create_user` tool — wraps `SyncUsersResource.create()`
- `update_user` tool — wraps `SyncUsersResource.update(id, ...)`, UNSET semantics for optional fields, `None` clears nullable fields
- `delete_user` tool — wraps `SyncUsersResource.delete(id)`
- Mount the new sub-server in `server.py` (no namespace, consistent with other sub-servers)

### Out of Scope
- Group management (separate resource, not part of this issue)
- MFA management
- Permission management beyond what `update_user` already supports via `user_permissions` / `groups`

---

## Acceptance Criteria

- [ ] `src/easypaperless_mcp/tools/users.py` exists and defines a `FastMCP` instance named `users`
- [ ] `list_users` returns a `ListResult[User]` and supports all filter/pagination parameters: `username_contains`, `username_exact`, `ordering`, `page`, `page_size`
- [ ] `get_user(id)` returns a `User` and raises a clear error when the user does not exist
- [ ] `create_user(username, ...)` returns the newly created `User`; `username` is the only required parameter; all other fields are optional
- [ ] `update_user(id, ...)` returns the updated `User`; only explicitly provided (non-UNSET) fields are sent; passing `None` to a nullable field clears it
- [ ] `delete_user(id)` returns nothing and raises a clear error when the user does not exist
- [ ] The `users` sub-server is mounted in `server.py`
- [ ] All tools pass mypy strict checks and ruff linting
- [ ] Unit tests cover all five tools (happy path + not-found error cases)

---

## Dependencies & Constraints

- Requires easypaperless >= 0.4.0 (already installed)
- Must follow the UNSET/None pattern established by `update_document`, `update_tag`, etc.
- Tool parameter names must match easypaperless API names exactly (e.g. `id`, not `user_id`)

---

## Priority

`Medium`

---

## Additional Notes

- `User` model fields: `id`, `username`, `email`, `password`, `first_name`, `last_name`, `date_joined`, `is_staff`, `is_active`, `is_superuser`, `groups` (list of int), `user_permissions` (list of str), `inherited_permissions` (read-only), `is_mfa_enabled` (read-only)
- Reference implementation: `tools/tags.py` and `tools/correspondents.py`

---

## QA

**Tested by:** QA Engineer
**Date:** 2026-03-20
**Commit:** 0f019da

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC: `src/easypaperless_mcp/tools/users.py` exists with `FastMCP` instance named `users` | File exists, `users = FastMCP("users")` | File present, instance defined on line 15 | ✅ Pass |
| 2 | AC: `list_users` returns `ListResult[User]` with all filter/pagination params | Supports `username_contains`, `username_exact`, `ordering`, `page`, `page_size` | All 5 params implemented and forwarded; None params omitted | ✅ Pass |
| 3 | AC: `get_user(id)` returns `User`, raises clear error when not found | Returns `User`; raises `NotFoundError` | Returns User; NotFoundError propagated | ✅ Pass |
| 4 | AC: `create_user(username, ...)` returns new `User`; only `username` required | username required, all other fields optional | Correct — only username required, 10 optional fields | ✅ Pass |
| 5 | AC: `update_user(id, ...)` returns updated `User`; UNSET semantics; None clears nullable | Only non-UNSET fields sent; None forwards to client | Correct UNSET pattern; None explicitly passed through | ✅ Pass |
| 6 | AC: `delete_user(id)` returns nothing; raises clear error when not found | Returns None; raises `NotFoundError` | Returns None; NotFoundError propagated | ✅ Pass |
| 7 | AC: `users` sub-server mounted in `server.py` | `mcp.mount(users)` present | Imported and mounted on line 75 of server.py | ✅ Pass |
| 8 | AC: All tools pass mypy strict checks | No mypy errors | `mypy --strict` reports: no issues found | ✅ Pass |
| 9 | AC: ruff linting passes | No ruff errors | `ruff check` reports: All checks passed | ✅ Pass |
| 10 | AC: Unit tests cover all five tools (happy path + not-found errors) | Tests for all 5 tools with happy path + error cases | 23 unit tests covering all tools, happy + error paths | ✅ Pass |
| 11 | Edge: `list_users()` with no params omits all optional kwargs | No extra kwargs forwarded to client | Verified by `test_list_users_omits_none_optional_params` | ✅ Pass |
| 12 | Edge: `update_user(id)` with only ID sends no extra kwargs | Empty kwargs dict to client | Verified by `test_update_user_no_extra_kwargs_when_only_id` | ✅ Pass |
| 13 | Edge: `update_user` with None for nullable fields clears them | `email=None`, `first_name=None`, `groups=None` forwarded | Verified — None values forwarded, not skipped | ✅ Pass |
| 14 | Integration: `list_users` returns `ListResult[User]` against live instance | Real API response mapped correctly | 3 integration tests pass against live paperless-ngx | ✅ Pass |
| 15 | Integration: `get_user` round-trip fetches correct user by ID | Fetched user ID matches listed user ID | Round-trip test passes | ✅ Pass |
| 16 | Regression: Full unit test suite (272 tests) unaffected | All existing tests still pass | 272 passed | ✅ Pass |
| 17 | Regression: Full integration test suite (30 tests) unaffected | All integration tests still pass | 30 passed | ✅ Pass |
| 18 | Note: Integration tests for create/update/delete not present | Read-only integration tests by design (convention matches other sub-servers) | Tests only cover list + get; create/update/delete covered by unit tests only | ✅ Acceptable |

### Bugs Found

None.

### Automated Tests

- Unit suite (tests/unit/test_users.py): 23 passed, 0 failed
- Full unit suite (tests/unit/): 272 passed, 0 failed
- Integration suite (tests/integration/test_users.py): 3 passed, 0 failed
- Full integration suite (tests/integration/): 30 passed, 0 failed
- mypy --strict: no issues
- ruff check: all checks passed
- Warning: `PydanticJsonSchemaWarning: Default value UNSET is not JSON serializable` — pre-existing across all sub-servers, not introduced by this issue

### Summary

- ACs tested: 9/9
- ACs passing: 9/9
- Bugs found: 0
- Recommendation: ✅ Ready to merge
