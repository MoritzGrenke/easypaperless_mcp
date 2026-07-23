# MCP Server for [SERVICE_NAME]

We build an MCP server that exposes functionality from [PYTHON_PACKAGE] (API wrapper for [SERVICE]) to AI agents.

## Techstack
- **MCP framework:** fastmcp>=3.0
- **Package manager:** uv
- **Testing:** pytest, pytest-asyncio
- **Linting/Formatting:** ruff
- **Type checking:** mypy (strict)

## Project Structure
```
src/[package_name]/
  __init__.py
  server.py          # FastMCP instance, mounts all sub-servers, middleware
  client.py          # get_client() — credential resolution + client factory
  tools/             # one sub-server per resource
    __init__.py
    models.py        # shared Pydantic models (ListResult etc.)
    [resource].py    # e.g. documents.py, tags.py, users.py

tests/
  conftest.py
  unit/
  integration/

dev/                 # issues & specs (from /requirements workflow)
```

## Development Workflow
1. `/requirements` — create feature spec from idea
2. `/architecture` — design structure, interfaces, tech decisions (no code)
3. `/dev` — implement features
4. `/test` — write tests
5. `/qa` — run tests, type-check, lint, edge cases, security audit
6. `/doc` — ensure high-quality documentation

## Architecture Patterns

### Transport
`MCP_TRANSPORT` env var selects the transport:
- `stdio` (default) — for local use with Claude Desktop or MCP Inspector
- `streamable-http` / `http` — HTTP server on `0.0.0.0:8000` for Docker/remote deployments

### Credential Resolution
Credentials always come from the MCP client, never stored server-side:
- **stdio:** env vars (e.g. `MY_SERVICE_TOKEN`) injected by the MCP client via the `env` key
- **HTTP:** `Authorization: Bearer <token>` header (preferred)

Implementation in `client.py`:
- `SERVER_URL` optionally locked server-side (e.g. Docker) — takes precedence over any client-supplied value
- `_request_token` / `_request_url` as `ContextVar` — set per-request by `CredentialMiddleware`
- `get_client()` reads from ContextVars — every tool calls `get_client()`

Error messages from `get_client()` must be actionable: tell the operator exactly where and how to configure the missing credential.

### Sub-Servers
- Each resource = one file + one `FastMCP` instance
- Mounted in `server.py` **without namespace**: `mcp.mount(resource)`
- Keep resources and sub-resources in separate files (e.g. `documents.py` and `document_notes.py`)

### Middleware
`CredentialMiddleware` sets ContextVars before each tool call via `on_call_tool`.
Optional: `PermissionMiddleware` filters the tool list based on user permissions via `on_list_tools` (convenience/UX feature, not a security boundary).

## Key Conventions

**Tool naming:** verb-first, singular/plural based on return cardinality
- `list_documents`, `get_document`, `create_tag`, `update_tag`, `delete_document`

**Parameter naming:** stay as close as possible to the underlying library's naming
- If the library uses `id`, don't rename it to `document_id` in the MCP tool

**Return types:**
- Return Pydantic models directly where meaningful (FastMCP serializes them)
- Use primitives only for simple cases (e.g. `list[str]`)
- All `list_*` tools return `ListResult[T]` — a shared wrapper with `count`, `items`, and optional `omitted_fields`

**UNSET pattern for update tools:**
- Declare `_UNSET: Any = UNSET` as a typed alias so mypy accepts it as default for any type
- Nullable fields default to `UNSET` (leave unchanged) — passing `None` clears the field
- Docstring must reflect this: *"Omit to leave unchanged, or pass None to clear."*

**Return field filtering (AI context efficiency):**
- List tools: compact default field set (e.g. only id, name, created)
- Get/update tools: configurable `return_fields` parameter
- Include `omitted_fields` + `omitted_fields_hint` in the response when fields are excluded
- Always force `id` into the response even if not in `return_fields`

**File size:** keep files small and focused — prefer many small files over one large file.

**Human-in-the-loop:** all workflows have user approval checkpoints.

## Product Context
@dev/PRD.md

## Feature Overview
@dev/issues/0000-general-index.md
