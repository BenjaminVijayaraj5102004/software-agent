import os
import json
import pytest
from pathlib import Path
from app.Mcp.remote_client import remote_mcp_client
from app.Mcp.config import auto_generate_remote_name, load_mcp_config, save_mcp_config, get_normalized_servers_list, add_remote_server_to_config
from app.Mcp.manager import mcp_manager
from app.Mcp.auth import mcp_auth, CredentialsStore


def test_is_remote_url():
    assert remote_mcp_client.is_remote_url("https://mcp.notion.com/mcp") is True
    assert remote_mcp_client.is_remote_url("http://localhost:8000/mcp") is True
    assert remote_mcp_client.is_remote_url("npx -y @modelcontextprotocol/server-filesystem .") is False
    assert remote_mcp_client.is_remote_url("uvx mcp-server-postgres") is False


def test_auto_generate_remote_name():
    assert auto_generate_remote_name("https://mcp.notion.com/mcp") == "notion"
    assert auto_generate_remote_name("https://api.github.com/mcp") == "github"
    assert auto_generate_remote_name("http://localhost:8000/mcp") == "localhost"


def test_credentials_store(tmp_path, monkeypatch):
    test_creds = tmp_path / "credentials.json"
    monkeypatch.setattr("app.Mcp.auth.CREDENTIALS_FILE", test_creds)

    CredentialsStore.save_token("https://mcp.notion.com/mcp", "test_notion_token_123")
    token = CredentialsStore.get_token("https://mcp.notion.com/mcp")
    assert token == "test_notion_token_123"


def test_remote_auth_headers(monkeypatch, tmp_path):
    test_creds = tmp_path / "credentials.json"
    monkeypatch.setattr("app.Mcp.auth.CREDENTIALS_FILE", test_creds)
    CredentialsStore.save_token("https://mcp.notion.com/mcp", "saved_token_456")

    headers = mcp_auth.resolve_headers("https://mcp.notion.com/mcp")
    assert headers.get("Authorization") == "Bearer saved_token_456"


@pytest.mark.asyncio
async def test_oauth_flow_and_token_retry(tmp_path, monkeypatch):
    test_creds = tmp_path / "credentials.json"
    monkeypatch.setattr("app.Mcp.auth.CREDENTIALS_FILE", test_creds)
    monkeypatch.setenv("MCP_BEARER_TOKEN", "mock_oauth_token_789")

    token, steps = await mcp_auth.start_oauth_flow("https://mcp.notion.com/mcp")
    assert token == "mock_oauth_token_789"
    assert CredentialsStore.get_token("https://mcp.notion.com/mcp") == "mock_oauth_token_789"
    assert any("Token" in s for s in steps)


@pytest.mark.asyncio
async def test_add_remote_server_config(tmp_path, monkeypatch):
    test_json = tmp_path / "mcp.json"
    monkeypatch.setattr("app.Mcp.config.MCP_CONFIG_FILE", test_json)

    add_remote_server_to_config("notion", "https://mcp.notion.com/mcp", transport="http")

    cfg = load_mcp_config()
    assert "mcpServers" in cfg
    assert "notion" in cfg["mcpServers"]
    assert cfg["mcpServers"]["notion"]["url"] == "https://mcp.notion.com/mcp"
    assert cfg["mcpServers"]["notion"]["transport"] == "http"

    servers = get_normalized_servers_list()
    assert len(servers) == 1
    assert servers[0]["name"] == "notion"
    assert servers[0]["url"] == "https://mcp.notion.com/mcp"
