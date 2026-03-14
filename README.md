# easypaperless-mcp

MCP server for [paperless-ngx](https://docs.paperless-ngx.com/) via the [easypaperless](https://pypi.org/project/easypaperless/) API wrapper.

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

Restart Claude Desktop after saving. The tools `list_documents`, `get_document`, and `search_documents` will appear in the Tools menu.

## Docker Deployment

Copy `.env.example` to `.env` and fill in your credentials, then:

```bash
docker compose up --build
```

The server runs on port `8000` using the `streamable-http` transport.
