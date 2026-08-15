import os
import json
import pytest
from pathlib import Path
from app.Mcp.config import (
    load_mcp_config,
    save_mcp_config,
    get_normalized_servers_list,
    parse_launch_command,
    auto_generate_name,
    add_server_to_config,
    remove_server_from_config,
)
from app.Mcp.process import resolve_executable, build_process_env
from app.Mcp.manager import mcp_manager


def test_parse_launch_command():
    name1, cmd1, args1 = parse_launch_command(["npx", "-y", "@modelcontextprotocol/server-filesystem", "C:\\Projects"])
    assert name1 == "filesystem"
    assert cmd1 == "npx"
    assert args1 == ["-y", "@modelcontextprotocol/server-filesystem", "C:\\Projects"]

    name2, cmd2, args2 = parse_launch_command(["uvx", "mcp-server-postgres"])
    assert name2 == "postgres"
    assert cmd2 == "uvx"
    assert args2 == ["mcp-server-postgres"]

    name3, cmd3, args3 = parse_launch_command(["docker", "run", "ghcr.io/github/github-mcp-server"])
    assert name3 == "github"
    assert cmd3 == "docker"
    assert args3 == ["run", "ghcr.io/github/github-mcp-server"]

    name4, cmd4, args4 = parse_launch_command("npx claude-code-templates@latest --mcp web/web-fetch")
    assert name4 == "web-fetch"
    assert cmd4 == "npx"
    assert args4 == ["claude-code-templates@latest", "--mcp", "web/web-fetch"]


@pytest.mark.asyncio
async def test_mcp_config_load_and_save(tmp_path, monkeypatch):
    test_json = tmp_path / "mcp.json"
    monkeypatch.setattr("app.Mcp.config.MCP_CONFIG_FILE", test_json)

    # Initial load creates default structure
    cfg = load_mcp_config()
    assert "mcpServers" in cfg or "servers" in cfg

    # Add a server
    add_server_to_config("filesystem", "npx", ["-y", "@modelcontextprotocol/server-filesystem", "."])

    servers = get_normalized_servers_list()
    assert len(servers) == 1
    assert servers[0]["name"] == "filesystem"
    assert servers[0]["command"] == "npx"
    assert servers[0]["enabled"] is True

    # Remove the server
    removed = remove_server_from_config("filesystem")
    assert removed is True

    final_servers = get_normalized_servers_list()
    assert len(final_servers) == 0


def test_build_process_env(monkeypatch):
    monkeypatch.setenv("TEST_TOKEN_XYZ", "secret123")
    res = build_process_env({"TOKEN": "${TEST_TOKEN_XYZ}"})
    assert res.get("TOKEN") == "secret123"
    assert "npm_config_cache" in res


@pytest.mark.asyncio
async def test_mcp_manager_doctor():
    res = await mcp_manager.doctor()
    assert "healthy" in res
    assert "steps" in res
    assert len(res["steps"]) >= 1
