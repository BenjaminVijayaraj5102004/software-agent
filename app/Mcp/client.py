import sys
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from .server import mcp_config


def create_mcp_client():
    """Creates and returns a MultiServerMCPClient instance."""
    return MultiServerMCPClient(mcp_config)


async def get_tools():
    """Fetch tools from the MCP server."""
    client = create_mcp_client()
    tools = await client.get_tools()
    return tools


if __name__ == "__main__":
    async def _test():
        tools = await get_tools()
        print(f"Found {len(tools)} tools")
        for tool in tools:
            print(tool.name)

    asyncio.run(_test())