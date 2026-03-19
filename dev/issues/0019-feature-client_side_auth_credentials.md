# [FEATURE] Client-side authentication credentials for secure MCP deployments

## Summary

Move `PAPERLESS_TOKEN` (and optionally `PAPERLESS_URL`) out of the server-side environment and into client-side configuration. This prevents unauthorized access to the MCP server by ensuring only MCP clients that supply valid credentials can use it.

---

## Problem Statement

Currently both `PAPERLESS_URL` and `PAPERLESS_TOKEN` are read from the server's environment (e.g. a Docker `.env` file). In a remote HTTP deployment, any client that can reach the server URL has full access to the paperless-ngx instance — no per-client authentication exists. Storing the token server-side also makes it hard to support multiple users or rotate credentials without restarting the server.

---

## Proposed Solution

Credentials are supplied by the MCP client, not the server operator:

- **`PAPERLESS_TOKEN`** is read exclusively from client-side configuration. The server must never read it from its own environment. There must be no documentation, example, or default behavior that encourages operators to set it server-side.
- **`PAPERLESS_URL`** follows a priority rule:
  - If the server operator has configured a URL server-side, that URL is used and client-supplied URL values are ignored. This supports locked-down deployments where the endpoint must not be overridable.
  - If no server-side URL is configured, the client-supplied URL is used, supporting flexible or multi-instance setups.

"Client-side" means the value is provided by the connecting MCP client per request or per session (e.g. passed as an MCP request header, a context variable, or an env var injected by a stdio client process).

The server must surface a clear, actionable error message when required credentials are missing from the client, guiding the operator to configure the MCP client rather than the server.

---

## User Stories

- As a server operator, I want the MCP server to require clients to supply their own token so that access is tied to the individual client, not to whoever can reach the server URL.
- As an MCP client user (e.g. Claude Desktop), I want to configure my paperless-ngx token in my own MCP client settings so that my credentials are never stored on the shared server.
- As a server operator, I want to optionally lock the paperless-ngx URL server-side so that clients cannot point the server at a different paperless instance.

---

## Scope

### In Scope
- `PAPERLESS_TOKEN` is sourced from the MCP client side only.
- `PAPERLESS_URL` priority logic: server-side wins if set; otherwise client-side is used.
- All documentation, README examples, and Docker configuration examples are updated to reflect the new approach. Server-side token configuration is removed from all examples and docs.
- A clear error is returned to the client when the token (or URL, if not set server-side) is missing.

### Out of Scope
- Multi-tenant support (each client using a different paperless instance simultaneously).
- Any changes to the easypaperless library itself.
- Authentication mechanisms beyond environment-variable-style credential passing (e.g. OAuth, API key headers in HTTP requests are an implementation concern).

---

## Acceptance Criteria
- [ ] The server does not read `PAPERLESS_TOKEN` from its own environment under any circumstances.
- [ ] If `PAPERLESS_URL` is set in the server environment it is used regardless of any client-supplied value.
- [ ] If `PAPERLESS_URL` is not set in the server environment, the client-supplied value is used.
- [ ] If the token is missing from the client-side context, a clear error message is returned that instructs the user to configure the MCP client, not the server.
- [ ] No README example, Docker Compose file, or configuration template includes `PAPERLESS_TOKEN` as a server-side variable.
- [ ] Existing tests are updated/extended to cover the new credential resolution logic.

---

## Dependencies & Constraints

- FastMCP 2.x must support a mechanism for the client to pass per-request or per-session values (e.g. via HTTP headers, MCP context, or stdio env injection). The concrete mechanism is an architecture/implementation concern.
- The singleton `_client` in `client.py` may need to become per-session or per-request if the token can differ between clients.

---

## Priority
`High`

---

## Additional Notes

- This change is a **breaking change** for any existing deployments that configure `PAPERLESS_TOKEN` server-side. Migration guidance must be included in the changelog and documentation.
- The `.env.example` / Docker Compose examples should be reviewed to ensure they do not mention `PAPERLESS_TOKEN` at all (or include a clear warning that it must not be set there).

---

## QA

**Tested by:** QA Engineer
**Date:** 2026-03-19
**Commit:** c20a81a (working tree — changes not yet committed)

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC1: Server never reads `PAPERLESS_TOKEN` from its own environment | `client.py` reads token only from ContextVar; `server.py` only reads token from env for stdio transport (which is client-injected, not server-set) | Correct — `get_client()` reads from ContextVar; middleware reads env only for stdio where the env is injected by the MCP client process | ✅ Pass |
| 2 | AC2: Server-side `PAPERLESS_URL` takes precedence over client-supplied value | `SERVER_URL or request.headers.get("x-paperless-url")` | Middleware uses `SERVER_URL or header`; unit test confirms server URL wins | ✅ Pass |
| 3 | AC3: Client-supplied `PAPERLESS_URL` is used when server has none set | `_request_url` set to header value when `SERVER_URL` is None | Middleware reads header value when `SERVER_URL` is None; unit test confirms | ✅ Pass |
| 4 | AC4: Clear error when token missing | RuntimeError with actionable message pointing to MCP client config | `get_client()` raises `RuntimeError` with `--header 'X-Paperless-Token: ...'` and `claude_desktop_config.json` guidance | ✅ Pass |
| 5 | AC5: No README/Docker/template includes `PAPERLESS_TOKEN` server-side | Token absent from all server-side config examples | `docker-compose.yml`, `docker-compose.ghcr.yml`, `.env.example` all omit token; README has `> Do NOT add PAPERLESS_TOKEN` warning | ✅ Pass |
| 6 | AC6: Existing tests updated for new credential resolution logic | All test suites pass | Unit tests (249/249 ✅) and integration tests (27/27 ✅) all pass | ✅ Pass |
| 7 | Edge: `get_client()` called without ContextVars set raises RuntimeError | RuntimeError with token guidance | Raises `RuntimeError: PAPERLESS_TOKEN is missing` with correct message | ✅ Pass |
| 8 | Edge: `get_client()` called with token but no URL raises RuntimeError | RuntimeError with URL guidance | Raises `RuntimeError: PAPERLESS_URL is missing` | ✅ Pass |
| 9 | Edge: ContextVars are reset after tool call even on exception | ContextVars revert to prior values | Unit test `test_contextvars_reset_on_exception` confirms finally-block cleanup | ✅ Pass |
| 10 | Edge: `SERVER_URL` locked — HTTP client cannot override via header | `captured_url == server-locked-url` even when header supplies different URL | Confirmed by unit test | ✅ Pass |
| 11 | Regression: `.env.example` does not mention `PAPERLESS_TOKEN` at all | No mention of token | `.env.example` contains explicit `NOTE: Do NOT add PAPERLESS_TOKEN here` comment | ✅ Pass |
| 12 | Integration: Tool calls resolve credentials via ContextVars during live test | Tools call paperless-ngx successfully | 27/27 integration tests pass — `set_contextvars` fixture seeds ContextVars from env vars | ✅ Pass |

### Bugs Found

None.

### Automated Tests
- Suite: `tests/unit` — **249 passed, 0 failed** ✅
- Suite: `tests/integration` — **27 passed, 0 failed** ✅
- mypy: **Success: no issues found in 12 source files** ✅
- ruff: **All checks passed** ✅

### Summary
- ACs tested: 6/6
- ACs passing: 6/6
- Bugs found: 0
- Recommendation: ✅ Ready to merge
