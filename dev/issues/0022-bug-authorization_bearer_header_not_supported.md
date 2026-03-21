# [BUG] `Authorization: Bearer` header not supported — `mcp-remote` auth fails

## Summary

The server reads the paperless-ngx token exclusively from the custom `X-Paperless-Token` HTTP header. `mcp-remote` — the standard tool for connecting Claude Desktop to remote MCP servers — sends credentials via the standard `Authorization: Bearer <token>` header. Because the server does not recognise this header, any `mcp-remote` client that injects the token via `--header Authorization:${AUTH_HEADER}` cannot authenticate, and all tool calls fail with a missing-token error.

---

## Environment

- **Version / Release:** current (post-0019)
- **Other relevant context:** Affects HTTP (`streamable-http`) transport only. Reproducible with any `mcp-remote` client that uses `--header Authorization:${AUTH_HEADER}`.

---

## Steps to Reproduce

1. Run the server with `MCP_TRANSPORT=streamable-http` (e.g. in Docker).
2. Configure Claude Desktop to connect via `mcp-remote`:
   ```json
   {
     "command": "npx",
     "args": ["-y", "mcp-remote", "https://<host>/mcp", "--header", "Authorization:${AUTH_HEADER}"],
     "env": { "AUTH_HEADER": "Bearer <paperless-token>" }
   }
   ```
3. Try calling any MCP tool (e.g. `list_documents`).

---

## Expected Behavior

The server extracts the paperless-ngx token from the `Authorization: Bearer <token>` header and processes the tool call normally, identical to receiving the token via `X-Paperless-Token`.

---

## Actual Behavior

The server finds no `X-Paperless-Token` header, leaves the token context variable unset, and raises:
```
RuntimeError: PAPERLESS_TOKEN is missing. Configure your MCP client to pass X-Paperless-Token: <token>.
```
No tool call succeeds.

---

## Impact

- **Severity:** `High`
- **Affected Users / Systems:** All users who connect Claude Desktop (or any other MCP client) to a remote easypaperless-mcp instance via `mcp-remote`. This is the primary recommended connection method for remote deployments; the bug effectively blocks the entire use case.

---

## Acceptance Criteria

- [x] When the HTTP request carries `Authorization: Bearer <token>`, the server extracts `<token>` and uses it as the paperless-ngx token — identical in behavior to receiving `X-Paperless-Token: <token>`.
- [x] `X-Paperless-Token` continues to work but is deprecated: a deprecation warning is included in the tool response or server log, instructing users to switch to `Authorization: Bearer <token>`.
- [x] If both headers are present, `Authorization: Bearer` takes precedence over `X-Paperless-Token`.
- [x] If the `Authorization` header is present but does not start with `Bearer ` (e.g. `Basic ...`), it is ignored for token extraction and the missing-token error is raised as usual.
- [x] The error message returned when the token is missing mentions both header options (`X-Paperless-Token` and `Authorization: Bearer`).
- [x] The `mcp-remote` Claude Desktop configuration example (from the README or docs) is added or updated to show the working `--header Authorization:${AUTH_HEADER}` pattern.
- [x] Unit tests cover: token from `Authorization: Bearer`, token from `X-Paperless-Token`, `Authorization: Bearer` precedence when both headers present, non-Bearer `Authorization` header ignored, deprecation warning emitted when `X-Paperless-Token` is used.
- [x] No other functionality is broken; all existing tests continue to pass.

---

## Additional Notes

- `mcp-remote` npm package: https://www.npmjs.com/package/mcp-remote
- The `Authorization` header is the standard OAuth2 / HTTP bearer-token mechanism; supporting it makes the server interoperable with any standard HTTP client, not just `mcp-remote`.
- Related issue: [0019 — Client-side authentication credentials](0019-feature-client_side_auth_credentials.md) (introduced `X-Paperless-Token`).

---

## QA

**Tested by:** QA Engineer
**Date:** 2026-03-21
**Commit:** 5d4b355 (+ uncommitted working-tree changes for this issue)

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC1: `Authorization: Bearer <token>` extracts token | Token used for paperless API | Token correctly extracted (server.py lines 63–65; `test_http_sets_token_from_authorization_bearer` passes) | ✅ Pass |
| 2 | AC2: `X-Paperless-Token` still works, deprecation warning logged | Works + WARNING in server log | Implemented; `test_http_x_paperless_token_emits_deprecation_warning` passes | ✅ Pass |
| 3 | AC3: Bearer takes precedence when both headers present | Bearer token used | `test_http_bearer_takes_precedence_over_x_paperless_token` passes | ✅ Pass |
| 4 | AC4: Non-Bearer `Authorization` header ignored, missing-token error raised | Token is None | `test_http_non_bearer_authorization_header_ignored` passes | ✅ Pass |
| 5 | AC5: Error message mentions both `X-Paperless-Token` and `Authorization: Bearer` | Both options in error text | Both headers listed in `get_client()` RuntimeError (client.py lines 62–67) | ✅ Pass |
| 6 | AC6: README updated with `--header Authorization:${AUTH_HEADER}` pattern | Working mcp-remote example shown | README updated (lines 80–93); Docker warning updated; config table updated | ✅ Pass |
| 7 | AC7: Unit tests cover all specified scenarios | 5 new unit tests present and passing | 6 new tests added, 14/14 unit tests in test_server.py pass | ✅ Pass |
| 8 | AC8: All existing tests continue to pass | No regressions | 293 unit + 33 integration pass | ✅ Pass |
| 9 | Edge: Non-Bearer Authorization + valid `X-Paperless-Token` (fallback behavior) | X-Paperless-Token used with deprecation warning | Implementation handles it (else-branch), but no test covers this combination | ⚠️ Untested |
| 10 | Linting: `ruff check src tests` clean | No errors | 9 × E402 violations in `server.py` — `logger` declaration placed between imports introduces new violations | ❌ Fail |
| 11 | CHANGELOG: Bearer auth documented in [0.2.0] Security section | Bearer support mentioned | Security section only mentions `X-Paperless-Token`; Bearer not listed | ❌ Fail |

### Bugs Found

#### BUG-001 — Ruff E402 violations introduced by logger placement [Severity: Low]

**Steps to reproduce:**
1. Run `uv run ruff check src tests`

**Expected:** No linting errors introduced by this change.
**Actual:** 9 × `E402 Module level import not at top of file` in `src/easypaperless_mcp/server.py`. The `logger = logging.getLogger(__name__)` declaration was inserted between the `from .client import ...` line and the `from .tools.*` imports, splitting the import block and triggering E402.
**Severity:** Low
**Notes:** Fix by moving `logger = logging.getLogger(__name__)` to after all top-level imports.

#### BUG-002 — CHANGELOG [0.2.0] Security section omits Bearer auth [Severity: Low]

**Steps to reproduce:**
1. Read `CHANGELOG.md` → section `[0.2.0]` → `Security`

**Expected:** An entry noting that `Authorization: Bearer <token>` is now the preferred/primary auth header for HTTP transport, with `X-Paperless-Token` deprecated.
**Actual:** The Security section reads: *"…`X-Paperless-Token` HTTP header for HTTP transport"* — no mention of Bearer auth or deprecation of X-Paperless-Token.
**Severity:** Low
**Notes:** Misleading to a reader who consults the changelog to understand the 0.2.0 security model.

### Automated Tests

- Suite: `tests/unit/` — 293 passed, 0 failed
- Suite: `tests/integration/` — 33 passed, 0 failed
- Type-check: `mypy src` — Success, no issues found in 14 source files
- Linter: `ruff check src tests` — **9 errors** (E402 in `server.py`)

### Summary

- ACs tested: 8/8 (+ 1 edge case flagged as untested)
- ACs passing: 6/8 (BUG-001 linting, BUG-002 changelog)
- Bugs found: 2 (Critical: 0, High: 0, Medium: 0, Low: 2)
- Recommendation: ❌ Needs fixes before merge — fix E402 linting violations and update CHANGELOG before committing.
