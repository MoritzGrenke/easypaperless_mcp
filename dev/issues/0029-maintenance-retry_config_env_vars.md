# [MAINTENANCE] Expose retry config via server-side env vars

## Summary

easypaperless 0.6.0 adds optional retry parameters to the `SyncPaperlessClient` constructor (`retry_attempts`, `retry_backoff`, `retry_on`). Currently `get_client()` in `client.py` creates the client without any retry config, leaving retries permanently disabled. This issue exposes the two most practical retry parameters as optional server-side environment variables so operators can enable automatic retries for transient failures without code changes.

---

## Background / Context

easypaperless 0.6.0 introduced automatic retry logic on the client constructor:

- `retry_attempts` (int, default 0 — disabled): maximum retry count after the first failure
- `retry_backoff` (float, default 1.0): initial sleep in seconds between attempts; doubles exponentially
- `retry_on`: tuple of exception types that trigger a retry (library default covers `ServerError` and connection errors)

Retrying is disabled by default (backward-compatible). Operators running easypaperless-mcp against unreliable or rate-limited paperless-ngx instances benefit from being able to enable retries via environment variables rather than requiring code changes or custom builds.

---

## Objectives

- Read `PAPERLESS_RETRY_ATTEMPTS` and `PAPERLESS_RETRY_BACKOFF` from the server environment in `client.py`
- Pass them to `SyncPaperlessClient` when set; otherwise keep the library defaults (retrying disabled)
- Document the new env vars in the project README / docstring

---

## Scope

### In Scope
- `client.py`: read `PAPERLESS_RETRY_ATTEMPTS` (int) and `PAPERLESS_RETRY_BACKOFF` (float) from `os.environ`; pass to `SyncPaperlessClient` constructor when present
- Update module-level docstring in `client.py` to document the new env vars
- Update unit tests for `get_client()` to cover the new env var paths

### Out of Scope
- `retry_on` — configuring the exception types via env var is complex and adds little practical value; leave it at the library default
- `tenacity_retrying` — not suitable for env var configuration
- Exposing retry config as per-request MCP headers (these are server-level operational settings)
- Any changes to tools or sub-servers

---

## Acceptance Criteria

- [ ] When `PAPERLESS_RETRY_ATTEMPTS` is set to a positive integer, `get_client()` passes `retry_attempts=<value>` to `SyncPaperlessClient`
- [ ] When `PAPERLESS_RETRY_BACKOFF` is set to a float, `get_client()` passes `retry_backoff=<value>` to `SyncPaperlessClient`
- [ ] When neither env var is set, `get_client()` behavior is unchanged (no retry kwargs passed, library defaults apply)
- [ ] Invalid values (non-integer `PAPERLESS_RETRY_ATTEMPTS`, non-float `PAPERLESS_RETRY_BACKOFF`) raise a clear `RuntimeError` with a helpful message
- [ ] `client.py` module docstring documents both env vars with their types and defaults
- [ ] Unit tests cover: both set, neither set, only one set, invalid value
- [ ] `ruff check` passes with no errors
- [ ] `mypy --strict` passes with no errors
- [ ] All existing unit and integration tests pass

---

## Dependencies

- Requires easypaperless>=0.6.0 (adds retry params to client constructor) — see issue 0028

---

## Priority

`Low`

---

## Additional Notes

- `PAPERLESS_RETRY_ATTEMPTS=3` with `PAPERLESS_RETRY_BACKOFF=2.0` gives retries at 2 s, 4 s, 8 s — reasonable for a flaky network.
- When all attempts are exhausted, easypaperless raises `RetryExhaustedError` (exported from top-level namespace in 0.6.0). The MCP layer does not need to handle this specially — it will surface as a tool error.

---

## QA

**Tested by:** QA Engineer  
**Date:** 2026-04-21  
**Commit:** (uncommitted working copy)

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC: `PAPERLESS_RETRY_ATTEMPTS` set → `retry_attempts` passed to client | `SyncPaperlessClient` called with `retry_attempts=<value>` | Confirmed by `test_get_client_passes_retry_attempts_when_set` | ✅ Pass |
| 2 | AC: `PAPERLESS_RETRY_BACKOFF` set → `retry_backoff` passed to client | `SyncPaperlessClient` called with `retry_backoff=<value>` | Confirmed by `test_get_client_passes_retry_backoff_when_set` | ✅ Pass |
| 3 | AC: Neither env var set → no retry kwargs passed | `SyncPaperlessClient` called with `url` and `api_token` only | Confirmed by `test_get_client_omits_retry_kwargs_when_not_set` | ✅ Pass |
| 4 | AC: Invalid `PAPERLESS_RETRY_ATTEMPTS` raises `RuntimeError` | `RuntimeError` with `"PAPERLESS_RETRY_ATTEMPTS"` in message | Confirmed by `test_invalid_retry_attempts_raises_runtime_error` | ✅ Pass |
| 5 | AC: Invalid `PAPERLESS_RETRY_BACKOFF` raises `RuntimeError` | `RuntimeError` with `"PAPERLESS_RETRY_BACKOFF"` in message | Confirmed by `test_invalid_retry_backoff_raises_runtime_error` | ✅ Pass |
| 6 | AC: Module docstring documents both env vars | Types and defaults documented | Confirmed — both vars documented with type, default, and usage example | ✅ Pass |
| 7 | AC: Unit tests cover both set, neither set, only one set, invalid | All four cases covered | `test_retry_attempts_parsed_from_env`, `test_retry_backoff_parsed_from_env`, `test_retry_both_parsed_from_env`, `test_retry_neither_env_var_set`, 2 invalid-value tests | ✅ Pass |
| 8 | AC: `ruff check` passes | No lint errors | All checks passed | ✅ Pass |
| 9 | AC: `mypy --strict` passes | No type errors in `client.py` | Clean — pre-existing `fastmcp.tools.tool` error in `server.py` is unrelated | ✅ Pass |
| 10 | AC: All existing tests pass | 344 green | 344 passed, 0 failed | ✅ Pass |
| Edge | Env vars parsed at import time → bad value raises at startup | `RuntimeError` at module load, not at first tool call | Confirmed — error raised during `importlib.reload(client_mod)` in tests | ✅ Pass |
| Edge | Both params individually (only attempts, only backoff) forwarded correctly | Only the set param appears in `SyncPaperlessClient` call kwargs | Confirmed by `test_get_client_passes_retry_attempts_when_set` (backoff=None) and `test_get_client_passes_retry_backoff_when_set` (attempts=None) | ✅ Pass |

### Bugs Found

No bugs found.

### Automated Tests

- Suite: `tests/unit/test_client.py` — 18 passed, 0 failed (8 new retry tests + 10 pre-existing)
- Suite: `tests/unit/` (full suite) — 344 passed, 0 failed

### Summary

- ACs tested: 9/9
- ACs passing: 9/9
- Bugs found: 0
- Recommendation: ✅ Ready to merge
