# [BUG] `list_correspondents` fails with "plain HTTP request sent to HTTPS port" on HTTPS instances

## Summary
When `PAPERLESS_URL` is set to an `https://` endpoint, calling `list_correspondents` fails with an nginx 400 error: "The plain HTTP request was sent to HTTPS port". Other tools such as `list_documents` and `list_tags` work correctly against the same HTTPS instance, so the issue is not a global HTTPS configuration problem but is specific to the correspondents endpoint (and potentially other untested tools).

---

## Environment
- **Version / Release:** current master
- **Python Version:** unknown
- **Paperless-ngx Version:** production instance (version unknown)
- **Platform / OS:** Windows (Claude Desktop)
- **Browser / Client (if applicable):** Claude Desktop
- **Other relevant context:** `PAPERLESS_URL` set to an `https://` production instance. `list_documents` and `list_tags` work correctly against the same instance and configuration.

---

## Steps to Reproduce
1. Configure Claude Desktop with `PAPERLESS_URL=https://<your-host>` and a valid `PAPERLESS_TOKEN`.
2. Start the MCP server.
3. Call `list_correspondents` with `{"page_size": 10}`.

---

## Expected Behavior
`list_correspondents` communicates with the paperless-ngx instance over TLS and returns a `ListResult` of correspondents.

---

## Actual Behavior
The tool returns an error containing an nginx HTML response:

```
Error calling tool 'list_correspondents': <html>
<head><title>400 The plain HTTP request was sent to HTTPS port</title></head>
<body>
<center><h1>400 Bad Request</h1></center>
<center>The plain HTTP request was sent to HTTPS port</center>
<hr><center>nginx</center>
</body>
</html>
```

`list_documents` and `list_tags` succeed against the same HTTPS instance, which suggests the correspondents API endpoint URL is being constructed incorrectly (e.g. the scheme is dropped or overridden) rather than there being a global TLS misconfiguration.

---

## Impact
- **Severity:** `High`
- **Affected Users / Systems:** Users connecting to a production (HTTPS) paperless-ngx instance. The correspondents sub-server is entirely non-functional for them. Other resource sub-servers may be affected too but have not been fully tested.

---

## Acceptance Criteria
- [ ] `list_correspondents` succeeds when `PAPERLESS_URL` uses `https://`.
- [ ] All other `list_*` and CRUD tools for correspondents are verified to work on an HTTPS instance.
- [ ] Any other tools that exhibit the same failure are fixed in the same change.
- [ ] `list_documents` and `list_tags` continue to work on HTTPS instances (no regression).
- [ ] A regression test (or documented manual test step) covers the HTTPS correspondents scenario.

---

## Additional Notes
- Since `list_documents` and `list_tags` work, the `SyncPaperlessClient` itself handles HTTPS correctly for those endpoints. Investigate how the correspondents endpoint URL is constructed in easypaperless compared to documents/tags — there may be a different base path, trailing slash, or redirect behaviour that causes the scheme to be lost.
- Related: `src/easypaperless_mcp/client.py` — the URL is passed directly from `PAPERLESS_URL` to `SyncPaperlessClient(url=url, ...)`.
- easypaperless API reference: https://moritzgrenke.github.io/easypaperless/easypaperless.html


## Status

Status is set to `External`. We could implement a difficult fix, but it was a lot easier to fix the bug in the underlying easypaperless package (see v0.3.1). So nothing to implement here. Issue closed.