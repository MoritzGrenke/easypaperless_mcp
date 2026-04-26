# [MAINTENANCE] Upgrade FastMCP to v3

## Summary

FastMCP 3 (stable since February 2026) introduces a first-class visibility system (`mcp.disable()` / `ctx.enable_components()`) that is required by issue 0023 (permission-based tool filtering). This issue upgrades the project from `fastmcp>=2.0` to `fastmcp>=3.0`, resolves any breaking changes, and verifies that both transport modes (`stdio` and `streamable-http`) continue to work correctly.

---

## Background / Context

FastMCP 3 adds several features relevant to this project:

- **Visibility system**: `mcp.disable(tags=...)` globally hides tools; `ctx.enable_components(tags=...)` re-enables them for a specific session. FastMCP automatically sends `ToolListChangedNotification` to affected sessions without touching others.
- **Per-component authorization**: `@tool(auth=...)` parameter for scope-based access control.
- **Session lifecycle hooks**: improved hooks for `list_tools` and session-connect events.

FastMCP 3 may introduce breaking changes to:
- Middleware API (currently used by `CredentialMiddleware` in `server.py`)
- Server setup / transport configuration
- Tool registration decorator signatures
- Sub-server mounting API

All of these must be verified and updated before issue 0023 can be implemented.

---

## Objectives

- Upgrade `fastmcp` dependency to `>=3.0` in `pyproject.toml`
- Identify and fix any breaking changes in `server.py`, `client.py`, and all tool modules
- Verify `stdio` and `streamable-http` transports continue to work
- Keep all existing tests green

---

## Scope

### In Scope
- `pyproject.toml`: bump `fastmcp>=2.0` → `fastmcp>=3.0`
- `server.py`: update `CredentialMiddleware`, server construction, transport setup, and sub-server mounting to the FastMCP 3 API
- Any tool module changes required by updated decorator or registration API
- Full test suite must pass after upgrade

### Out of Scope
- Using any FastMCP 3 features (visibility system, per-component auth, etc.) — that is the responsibility of issue 0023
- Any functional changes to tools, credential flow, or transport behavior

---

## Acceptance Criteria

- [ ] `pyproject.toml` declares `fastmcp>=3.0`
- [ ] `server.py` compiles and starts without errors under FastMCP 3
- [ ] `CredentialMiddleware` works correctly under the FastMCP 3 middleware API for both `stdio` and `streamable-http` transports
- [ ] All sub-servers mount and register their tools without errors
- [ ] `ruff check` passes with no errors
- [ ] `mypy --strict` passes with no new errors introduced by this upgrade
- [ ] All existing unit and integration tests pass

---

## Dependencies

None. This is a prerequisite for issue 0023.

---

## Priority

`High`

---

## Additional Notes

- FastMCP 3 release notes / changelog should be reviewed before implementation to identify all breaking changes: https://github.com/jlowin/fastmcp
- If the FastMCP 3 middleware API has changed significantly, `CredentialMiddleware` in `server.py` is the most likely area requiring rework.
- The FastMCP 3 visibility system (`mcp.disable()`, `ctx.enable_components()`) should be left untouched in this issue — do not introduce partial permission logic here.

---

## QA

**Tested by:** QA Engineer  
**Date:** 2026-04-26  
**Commit:** 61a8d88  
**FastMCP installed (venv):** 3.1.0 | **FastMCP installed (system Python / mypy):** 3.2.4

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC1: `pyproject.toml` declares `fastmcp>=3.0` | Dependency pinned to `>=3.0` | `fastmcp>=3.0` present in working-tree diff | ✅ Pass |
| 2 | AC2: `server.py` compiles and starts without errors | Module loads cleanly | `python -c "import easypaperless_mcp.server"` succeeds (1 pre-existing Pydantic warning about `UNSET`, not new) | ✅ Pass |
| 3 | AC3: `CredentialMiddleware` works under FastMCP 3 middleware API | All middleware imports resolve; middleware accepted by `FastMCP(middleware=[...])` | `fastmcp.server.middleware`, `fastmcp.server.context._current_transport`, `fastmcp.server.dependencies.get_http_request` all import successfully | ✅ Pass |
| 4 | AC4: All sub-servers mount and register tools without errors | 10 sub-servers mount; all tools visible | Server module loads and mounts all sub-servers without error | ✅ Pass |
| 5 | AC5: `ruff check` passes | No lint errors | `ruff check src/ tests/` → `All checks passed!` | ✅ Pass |
| 6 | AC6: `mypy --strict` passes with no new errors | No type errors | `mypy src/ --strict` → 1 error: `Cannot find implementation or library stub for module named "fastmcp.tools.tool"` in `server.py:7` | ❌ Fail |
| 7 | AC7: All existing unit and integration tests pass | 344 unit tests green; integration tests skipped (no live infra) | 344 passed, 40 skipped, 1 warning | ✅ Pass |
| 8 | Edge: `document_history.py` unused import removed | File clean under ruff | `AuditLogActor` removed from imports; ruff passes | ✅ Pass |
| 9 | Edge: Pydantic warning about UNSET not serializable | Warning should be pre-existing, not new | Warning present — originates from easypaperless, pre-dates this upgrade | ✅ Pass (pre-existing) |

### Bugs Found

#### BUG-001 — `mypy --strict` fails: `fastmcp.tools.tool` not found after FastMCP 3 upgrade [Severity: High]

**Steps to reproduce:**
1. Ensure working tree has `fastmcp>=3.0` in `pyproject.toml` (already the case)
2. Run `python -m mypy src/ --strict`

**Expected:** No new mypy errors  
**Actual:** `src\easypaperless_mcp\server.py:7: error: Cannot find implementation or library stub for module named "fastmcp.tools.tool" [import-not-found]`

**Root cause:** FastMCP renamed `fastmcp/tools/tool.py` → `fastmcp/tools/base.py` in 3.2.x. The package adds a `sys.modules` shim in `fastmcp/tools/__init__.py` so `from fastmcp.tools.tool import ToolResult` continues to work at **runtime**, but mypy cannot resolve `sys.modules` manipulation — it needs a real file on disk.

**Fix:** In `server.py:7`, change:
```python
from fastmcp.tools.tool import ToolResult
```
to:
```python
from fastmcp.tools import ToolResult
```
`ToolResult` is exported from `fastmcp.tools.__init__` in all FastMCP 3.x versions.

**Severity:** High — AC6 explicitly requires `mypy --strict` to pass; this is a new error introduced by the upgrade.

### Automated Tests

- Unit suite (pytest): 344 passed, 40 skipped, 1 warning — all green
- Integration tests: 40 skipped — requires `PAPERLESS_URL` and `PAPERLESS_TOKEN` env vars; untested in this QA run
- `ruff check src/ tests/`: All checks passed
- `mypy src/ --strict`: 1 error (see BUG-001)

### Summary

- ACs tested: 7/7
- ACs passing: 6/7
- Bugs found: 1 (Critical: 0, High: 1, Medium: 0, Low: 0)
- Recommendation: ❌ Needs fixes before merge — fix `server.py:7` import path to resolve the mypy error, then re-run `mypy --strict` to confirm clean.
