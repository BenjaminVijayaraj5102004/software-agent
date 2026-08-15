import os
import json
import pytest
from pathlib import Path
from app.Mcp.installer import mcp_installer
from app.Mcp.importer import mcp_importer
from app.Mcp.config import load_mcp_config, save_mcp_config, get_normalized_servers_list


def test_is_git_url():
    assert mcp_installer.is_git_url("https://github.com/user/repo") is True
    assert mcp_installer.is_git_url("git@github.com:user/repo.git") is True
    assert mcp_installer.is_git_url("npx @modelcontextprotocol/server-filesystem .") is False


def test_is_local_dir(tmp_path):
    d = tmp_path / "my_mcp"
    d.mkdir()
    assert mcp_installer.is_local_dir(str(d)) is True
    assert mcp_installer.is_local_dir("./non_existent_folder_123") is True
    assert mcp_installer.is_local_dir("uvx mcp-server-postgres") is False


def test_detect_project_type(tmp_path):
    node_dir = tmp_path / "node_proj"
    node_dir.mkdir()
    (node_dir / "package.json").write_text("{}")
    assert mcp_installer.detect_project_type(node_dir) == "node"

    py_dir = tmp_path / "py_proj"
    py_dir.mkdir()
    (py_dir / "pyproject.toml").write_text("[project]")
    assert mcp_installer.detect_project_type(py_dir) == "python"


def test_importer(tmp_path, monkeypatch):
    test_mcp_json = tmp_path / "mcp.json"
    monkeypatch.setattr("app.Mcp.config.MCP_CONFIG_FILE", test_mcp_json)

    config_to_import = tmp_path / "claude_desktop_config.json"
    config_to_import.write_text(json.dumps({
        "mcpServers": {
            "test_server": {
                "command": "python",
                "args": ["server.py"]
            }
        }
    }))

    res = mcp_importer.import_config_file(str(config_to_import))
    assert res["status"] == "success"
    assert "test_server" in res["imported"]

    servers = get_normalized_servers_list()
    assert len(servers) == 1
    assert servers[0]["name"] == "test_server"
