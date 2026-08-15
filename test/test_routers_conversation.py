import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_conversation(client: AsyncClient, access_token: str):
    """Test creating a conversation with an authorized token."""
    response = await client.post(
        "/api/conversation/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"title": "Architecting FastAPI Backend"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["title"] == "Architecting FastAPI Backend"


@pytest.mark.asyncio
async def test_create_conversation_unauthorized(client: AsyncClient):
    """Test creating a conversation fails without authentication."""
    response = await client.post(
        "/api/conversation/",
        json={"title": "Unauthorized attempt"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_conversations_list(client: AsyncClient, access_token: str, conversation_id: str):
    """Test listing user conversations."""
    response = await client.get(
        "/api/conversation",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    conversations = response.json()
    assert isinstance(conversations, list)
    assert any(c["id"] == conversation_id for c in conversations)


@pytest.mark.asyncio
async def test_get_conversation_by_id(client: AsyncClient, access_token: str, conversation_id: str):
    """Test retrieving a specific conversation by ID."""
    response = await client.get(
        f"/api/conversation/{conversation_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == conversation_id


@pytest.mark.asyncio
async def test_get_conversation_not_found(client: AsyncClient, access_token: str):
    """Test retrieving non-existent conversation returns 404."""
    random_id = str(uuid.uuid4())
    response = await client.get(
        f"/api/conversation/{random_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Conversation not found"


@pytest.mark.asyncio
async def test_delete_conversation(client: AsyncClient, access_token: str):
    """Test deleting a conversation by ID."""
    # First create a conversation to delete
    create_res = await client.post(
        "/api/conversation/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"title": "To be deleted"},
    )
    conv_id = create_res.json()["id"]
    
    # Delete
    del_res = await client.delete(
        f"/api/conversation/{conv_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert del_res.status_code == 200
    assert del_res.json()["message"] == "Conversation deleted successfully"
    
    # Verify 404 on subsequent get
    get_res = await client.get(
        f"/api/conversation/{conv_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert get_res.status_code == 404
