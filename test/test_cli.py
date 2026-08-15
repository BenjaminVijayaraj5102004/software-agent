import uuid
from unittest.mock import MagicMock
import pytest

from app.cli.auth import register_cmd, login_cmd, me_cmd
from app.cli.conversation import (
    create_conversation_cmd,
    list_conversations_cmd,
    get_conversation_cmd,
    delete_conversation_cmd,
    resolve_conversation_id,
    get_user_from_token,
)
from app.cli.github_cli import get_github_client, user_info_cmd, search_repos_cmd
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_cli_register_and_login_flow(db_session):
    """Test CLI register and login commands."""
    unique_email = f"cli_user_{uuid.uuid4().hex[:6]}@gmail.com"
    passw = "clipassword123"
    
    reg_res = await register_cmd(email=unique_email, password=passw, silent=True)
    assert reg_res["status"] == "success"
    assert reg_res["user"]["email"] == unique_email
    
    login_res = await login_cmd(email=unique_email, password=passw, silent=True)
    assert login_res["status"] == "success"
    assert "access_token" in login_res
    
    # Test me_cmd with token
    token = login_res["access_token"]
    me_res = await me_cmd(token=token, silent=True)
    assert me_res["status"] == "success"
    assert me_res["user"]["email"] == unique_email


@pytest.mark.asyncio
async def test_cli_auth_invalid_login():
    """Test CLI login with invalid credentials."""
    login_res = await login_cmd(email="does_not_exist@gmail.com", password="bad", silent=True)
    assert login_res["status"] == "error"
    assert "Invalid email" in login_res["detail"]


@pytest.mark.asyncio
async def test_cli_me_invalid_token():
    """Test CLI me_cmd with missing or invalid token."""
    res = await me_cmd(token="bad_token", silent=True)
    assert res["status"] == "error"


@pytest.mark.asyncio
async def test_cli_conversation_lifecycle(db_session, test_user):
    """Test CLI conversation creation, listing, retrieval, and deletion."""
    token = create_access_token(data={"sub": test_user["email"]})
    
    # Create conversation
    create_res = await create_conversation_cmd(
        title="CLI Test Conversation",
        token=token,
        silent=True
    )
    assert create_res["status"] == "success"
    conv_id = create_res["conversation"]["id"]
    
    # List conversations
    list_res = await list_conversations_cmd(token=token, silent=True)
    assert list_res["status"] == "success"
    assert len(list_res["conversations"]) >= 1
    
    # Get conversation
    get_res = await get_conversation_cmd(conversation_id=conv_id, token=token, silent=True)
    assert get_res["status"] == "success"
    assert get_res["conversation"]["title"] == "CLI Test Conversation"
    
    # Delete conversation
    del_res = await delete_conversation_cmd(conversation_id=conv_id, token=token, silent=True)
    assert del_res["status"] == "success"


@pytest.mark.asyncio
async def test_cli_resolve_conversation_id(db_session, test_user):
    """Test resolve_conversation_id with index and UUID strings."""
    user_id = test_user["user"].id
    
    # Resolve None or empty
    assert await resolve_conversation_id(db_session, user_id, None) is None
    assert await resolve_conversation_id(db_session, user_id, "") is None
    
    # Resolve invalid index
    assert await resolve_conversation_id(db_session, user_id, "9999") is None
    
    # Resolve standard UUID
    test_uuid = str(uuid.uuid4())
    resolved = await resolve_conversation_id(db_session, user_id, test_uuid)
    assert resolved == test_uuid


def test_cli_github_helpers(monkeypatch):
    """Test GitHub CLI functions with mocked PyGithub client."""
    mock_gh = MagicMock()
    mock_user = MagicMock()
    mock_user.login = "octocat"
    mock_user.name = "The Octocat"
    mock_user.email = "octocat@github.com"
    mock_user.public_repos = 8
    mock_user.followers = 42
    mock_user.following = 0
    mock_user.html_url = "https://github.com/octocat"
    mock_gh.get_user.return_value = mock_user
    
    monkeypatch.setattr("app.cli.github_cli.get_github_client", lambda token=None: mock_gh)
    
    res = user_info_cmd(token="dummy_token", json_output=False)
    assert res["status"] == "success"
    assert res["user"]["login"] == "octocat"
