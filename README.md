# easypaperless-mcp

MCP server for [paperless-ngx](https://docs.paperless-ngx.com/) built on top of the [easypaperless](https://pypi.org/project/easypaperless/) Python API wrapper.

Exposes **60 tools** across 10 resource sub-servers so AI agents can read, search, create, update, and delete every major paperless-ngx resource.

## Features

- **Documents** — list (with rich filtering), get, update, delete, upload, bulk operations, metadata
- **Document History** — retrieve the full audit log for any document (who changed what and when)
- **Document Notes** — list, create, delete per-document notes
- **Tags** — full CRUD + bulk delete and bulk permissions
- **Correspondents** — full CRUD + bulk delete and bulk permissions
- **Document Types** — full CRUD + bulk delete and bulk permissions
- **Custom Fields** — full CRUD
- **Storage Paths** — full CRUD + bulk delete and bulk permissions
- **Users** — full CRUD (list, get, create, update, delete)
- **Trash** — list, restore, and permanently empty trashed documents
- Token-efficient responses: `list_documents` and `get_document` ship a compact default field set; pass `return_fields` to customise
- All list tools return a `count` field with the total number of matching records in paperless-ngx (not just the current page)
- Client-side auth: credentials are passed per-request (env vars for stdio, HTTP headers for HTTP transport) — never stored server-side
- Transports: `stdio` (local / Claude Desktop) and `streamable-http` (Docker / remote)

## Requirements

- Python 3.11 or newer
- [uv](https://github.com/astral-sh/uv) package manager
- A running paperless-ngx instance with an API token

## Claude Desktop Setup (stdio — local)

In Claude Desktop: Settings -> Developer -> Edit Config
Add the following to your Claude Desktop config file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "easypaperless": {
      "command": "uv",
      "args": [
        "--project",
        "path_to_your_project_folder/easypaperless_mcp",
        "run",
        "easypaperless-mcp"
      ],
      "env": {
        "PAPERLESS_URL": "http://your-host:port",
        "PAPERLESS_TOKEN": "your-token"
      }
    }
  }
}
```

Restart Claude Desktop after saving.

## Connecting Claude Desktop to a Remote Docker Server (HTTP)

So far I wasn't successful to connect the mcp server (in Docker) directly to Claude Desktop. The following worked for me:
If the server runs in Docker, use `mcp-remote` as a local stdio bridge.  Pass your credentials as request headers.

**Requirements:** Node.js must be installed.

In Claude Desktop: Settings -> Developer -> Edit Config
Add the following to your Claude Desktop config file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "easypaperless": {
      "command": "npx",
      "args": [
        "-y", "mcp-remote",
        "https://your-server-url/mcp",
        "--header", "Authorization:${AUTH_HEADER}",
        "--header", "X-Paperless-URL: http://your-paperless-host:8000"
      ],
      "env": {
        "AUTH_HEADER": "Bearer your-token"
      }
    }
  }
}
```

Omit `--header X-Paperless-URL` if `PAPERLESS_URL` is already set in the server's Docker environment (Recommended).

Restart Claude Desktop after saving. On first start, `npx` downloads `mcp-remote` automatically.

Read more about: [mcp-remote](https://www.npmjs.com/package/mcp-remote)

## Docker Deployment

Copy `.env.example` to `.env`:

```
# Optionally lock the paperless-ngx URL for all clients:
# PAPERLESS_URL=http://your-paperless-ngx-host:8000

MCP_TRANSPORT=streamable-http
```

Then start the server:

```bash
docker compose up --build
```

The MCP server listens on port `8000` using the `streamable-http` transport.

> **Do NOT add `PAPERLESS_TOKEN` to `.env` or the Docker environment.** The token must be supplied by each MCP client via the `Authorization: Bearer <token>` request header (see above).

## Server Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PAPERLESS_URL` | no | Lock the paperless-ngx URL for all clients. If unset, each client supplies it. |
| `MCP_TRANSPORT` | no | `stdio` (default) or `streamable-http` |
| `PAPERLESS_RETRY_ATTEMPTS` | no | Maximum retry count after the first failure (integer, default: 0 — disabled). Set to a positive integer to enable automatic retries for transient errors. |
| `PAPERLESS_RETRY_BACKOFF` | no | Initial sleep in seconds between retry attempts, doubling exponentially (float, default: 1.0). Only relevant when `PAPERLESS_RETRY_ATTEMPTS` > 0. |

## MCP Client Configuration

| Header / env var | Transport | Required | Description |
|------------------|-----------|----------|-------------|
| `PAPERLESS_TOKEN` env var | stdio | yes | paperless-ngx API token (set in Claude Desktop `"env"` config) |
| `PAPERLESS_URL` env var | stdio | yes | paperless-ngx base URL (set in Claude Desktop `"env"` config) |
| `Authorization: Bearer <token>` header | HTTP | yes | paperless-ngx API token (preferred; passed via `mcp-remote --header`) |
| `X-Paperless-Token` header | HTTP | yes (deprecated) | paperless-ngx API token — use `Authorization: Bearer` instead |
| `X-Paperless-URL` header | HTTP | if server URL not locked | paperless-ngx base URL (passed via `mcp-remote --header`) |

## Tool Reference

See [`docs/tool-reference.md`](docs/tool-reference.md) for the full list of tools with parameters.

## Development

```bash
# Install dependencies (including dev extras)
uv sync

# Run tests
uv run pytest

# Lint
uv run ruff check src tests

# Type-check
uv run mypy src
```
