# easypaperless-mcp

MCP server for [paperless-ngx](https://docs.paperless-ngx.com/) built on top of the [easypaperless](https://pypi.org/project/easypaperless/) Python API wrapper.

Exposes **51 tools** across 7 resource sub-servers so AI agents can read, search, create, update, and delete every major paperless-ngx resource.

## Features

- **Documents** — list (with rich filtering), get, update, delete, upload, bulk operations, metadata
- **Document Notes** — list, create, delete per-document notes
- **Tags** — full CRUD + bulk delete and bulk permissions
- **Correspondents** — full CRUD + bulk delete and bulk permissions
- **Document Types** — full CRUD + bulk delete and bulk permissions
- **Custom Fields** — full CRUD
- **Storage Paths** — full CRUD + bulk delete and bulk permissions
- Token-efficient responses: `list_documents` and `get_document` ship a compact default field set; pass `return_fields` to customise
- All list tools return a `count` field with the total number of matching records in paperless-ngx (not just the current page)
- Transports: `stdio` (local / Claude Desktop) and `streamable-http` (Docker / remote)

## Requirements

- Python 3.11 or newer
- [uv](https://github.com/astral-sh/uv) package manager
- A running paperless-ngx instance with an API token

## Claude Desktop Setup

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

## Connecting Claude Desktop to a Remote Docker Server

If the server runs in Docker and you want to connect Claude Desktop to it via HTTP, the "Custom MCP Server" connector in the Claude Desktop UI does not work reliably. Use `mcp-remote` as a local stdio bridge instead.

**Requirements:** Node.js must be installed.

Add the following to your Claude Desktop config file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "easypaperless": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://your-server-url/mcp"]
    }
  }
}
```

Restart Claude Desktop after saving. On first start, `npx` downloads `mcp-remote` automatically.

## Docker Deployment

Copy `.env.example` to `.env` and fill in your credentials:

```
PAPERLESS_URL=http://your-paperless-ngx-host:8000
PAPERLESS_TOKEN=your-api-token-here
MCP_TRANSPORT=streamable-http
```

Then start the server:

```bash
docker compose up --build
```

The MCP server listens on port `8000` using the `streamable-http` transport.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PAPERLESS_URL` | yes | Base URL of your paperless-ngx instance (e.g. `http://localhost:8000`) |
| `PAPERLESS_TOKEN` | yes | paperless-ngx API token |
| `MCP_TRANSPORT` | no | `stdio` (default) or `streamable-http` |

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
