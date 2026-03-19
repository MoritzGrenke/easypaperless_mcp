"""Introspect all registered MCP tools and print a Markdown reference table."""

import asyncio
import inspect
import os
import sys

# Prevent real client initialization
os.environ.setdefault("PAPERLESS_URL", "http://localhost")
os.environ.setdefault("PAPERLESS_TOKEN", "dummy")

sys.path.insert(0, "src")

from easypaperless_mcp.server import mcp  # noqa: E402


async def main() -> None:
    tools = await mcp.list_tools()

    print(f"# Tool Reference ({len(tools)} tools)\n")

    for tool in sorted(tools, key=lambda t: t.name):
        print(f"## `{tool.name}`")

        name = tool.name
        if tool.description:
            first_para = tool.description.split("\n\n")[0].strip()
            print(f"\n{first_para}\n")

        schema = tool.parameters or {}
        props: dict = schema.get("properties", {})
        required: list = schema.get("required", [])

        if props:
            print("| Parameter | Type | Required | Description |")
            print("|-----------|------|----------|-------------|")
            for param, info in props.items():
                ptype = info.get("type") or info.get("anyOf", [{}])[0].get("type", "any")
                is_required = "yes" if param in required else "no"
                desc = info.get("description", "").replace("\n", " ")
                print(f"| `{param}` | `{ptype}` | {is_required} | {desc} |")
        else:
            print("_No parameters._")

        print()


asyncio.run(main())
