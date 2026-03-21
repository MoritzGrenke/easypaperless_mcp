# [FEATURE] Permission-based tool filtering — hide tools the authenticated user cannot use

## Summary

When an MCP client connects with a paperless-ngx API token, that token is tied to a specific user who may have limited Django permissions. The MCP server should resolve those permissions at session start and suppress any tools the user is not allowed to invoke. This prevents AI agents from discovering and attempting actions that will always be rejected by paperless-ngx.

---

## Problem Statement

Every user in paperless-ngx has a fine-grained Django permission set (e.g. `add_document`, `change_tag`, `delete_correspondent`). Currently the MCP server exposes all tools to every authenticated client regardless of what the underlying user is actually allowed to do. This leads to two problems:

1. **Noise for the AI agent** — the agent may attempt operations (e.g. delete a document) that are guaranteed to fail, wasting tokens and causing confusion.
2. **False affordance** — the tool list implies capabilities the user does not have, undermining trust in the server's tool descriptions.

---

## Proposed Solution

On session start (first tool call), the server resolves the current user's Django permissions using the supplied API token. It compares those permissions against a static mapping of `tool name → required Django permission`. Any tool whose required permission is absent from the user's effective permission set is hidden from the client for the remainder of the session.

The lookup result is cached for the session lifetime so it is performed at most once per connection.

If the lookup fails for any reason (network error, token not associated with any known user, permission data unavailable), the server surfaces an actionable error and does not allow any tool call to proceed.

> **Implementation note:** The mechanism for resolving which user corresponds to the provided token (e.g. a `/api/profile/` endpoint, or matching against `users.list()` output) must be confirmed during the design phase. Token values are not exposed by the users list API, so a dedicated "current user" endpoint may be required.

---

## User Stories

- As an AI agent, I want to only see tools I am actually permitted to use so that I do not waste calls attempting forbidden operations.
- As a paperless-ngx administrator, I want read-only users connecting via MCP to be unable to discover or invoke write/delete tools so that the permission model I configured in paperless-ngx is respected end-to-end.
- As a server operator, I want the permission check to be performed once per session so that normal tool use is not slowed down by repeated API calls.

---

## Scope

### In Scope
- Permission resolution at session start for both `stdio` and `streamable-http` transports.
- A static mapping of every MCP tool to the Django permission it requires (e.g. `delete_document` → `paperless.delete_document`).
- Per-session caching of the resolved permission set (no re-fetch within a session).
- Tools with no write/delete semantics (read-only list/get tools) require only the corresponding `view_*` permission.
- If the permission check fails, the server returns a clear error and no tool calls are processed.
- Unit tests covering: all permission tiers (view/add/change/delete), the caching behaviour, and the error path.

### Out of Scope
- Object-level permissions (e.g. per-document owner/viewer assignments) — only model-level Django content-type permissions are considered.
- Mid-session permission refresh (permissions are fixed for the session lifetime).
- Any changes to the easypaperless library.
- Changing how credentials are supplied (that is handled by issue 0019/0022).

---

## Acceptance Criteria

- [ ] On the first tool call of a session, the server looks up the effective Django permissions of the authenticated user and caches them for the session.
- [ ] A static `TOOL_PERMISSIONS` mapping exists that covers every tool registered in the MCP server, associating each tool with the Django permission required to invoke it.
- [ ] Tools whose required permission is absent from the user's effective set are not advertised to the client (hidden, not just blocked after the fact).
- [ ] If the permission lookup fails (any error), the server returns a descriptive error message and does not proceed with the tool call.
- [ ] A superuser or a user with all relevant permissions sees the full tool list unchanged.
- [ ] A user with only `view_*` permissions sees only list/get tools; all create, update, delete, and bulk-action tools are hidden.
- [ ] The permission check is performed at most once per session; subsequent tool calls in the same session use the cached result without additional API calls.
- [ ] Both `stdio` and `streamable-http` transports apply the same filtering logic.
- [ ] All existing tests continue to pass.
- [ ] New unit tests cover the happy path (full permissions), the read-only path, the superuser path, the cache hit path, and the error/fail path.

---

## Dependencies & Constraints

- The paperless-ngx API does not expose which user a token belongs to — it is not possible to resolve the current user from the token alone. Therefore the client must explicitly supply the username alongside the token (e.g. as an additional header or env var). The server uses the username to look up the user via `users.list()` and read their permissions.
- FastMCP must support a mechanism to conditionally register or suppress tools at session/connection time. If dynamic tool registration is not supported, an alternative approach (e.g. tools that return a "permission denied" error) may be needed — to be resolved during architecture.
- Depends on issue 0019 (client-side auth) and issue 0022 (Bearer header) being in place so the token is reliably available when the permission check runs.

---

## Priority
`High`

---

## Additional Notes

- The Django permission codenames follow the pattern `<app>.<action>_<model>`, e.g. `paperless.delete_document`, `paperless.add_tag`, `paperless.change_correspondent`. The exact app label used by paperless-ngx must be verified.
- The `is_superuser` flag should bypass all permission checks — superusers see all tools.
- Related issues: 0019 (client-side credentials), 0022 (Bearer auth header).