import os
import pytest
import app.Agents.main as main_module
from app.Agents.dynamic_mcp_agents import build_dynamic_mcp_subagents
from app.Agents.main import init_agent
from app.Mcp.config import add_server_to_config, remove_server_from_config


@pytest.mark.asyncio
async def test_build_dynamic_mcp_subagents(tmp_path, monkeypatch):
    test_json = tmp_path / "mcp.json"
    monkeypatch.setattr("app.Mcp.config.MCP_CONFIG_FILE", test_json)

    subagents = await build_dynamic_mcp_subagents()
    assert isinstance(subagents, list)


@pytest.mark.asyncio
async def test_main_supervisor_init(tmp_path, monkeypatch):
    test_json = tmp_path / "mcp.json"
    monkeypatch.setattr("app.Mcp.config.MCP_CONFIG_FILE", test_json)

    main_module.app = None
    main_app = await init_agent()
    assert main_app is not None
