# tools.py

from ..Mcp.client import get_tools

async def get_filtered_tools():
    all_tools = await get_tools()

    target_names = {
        "search_repositories",
        "search_code",
        "search_users",
        "get_file_contents",
    }

    return [t for t in all_tools if t.name in target_names]

