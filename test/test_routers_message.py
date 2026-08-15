import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_message_with_mocked_agent(client: AsyncClient, access_token: str, conversation_id: str, monkeypatch):
    """Test posting a user message and receiving the AI assistant's generated response."""
    
    def mock_chat(conversation_history, user_name=None, conversation_id=None):
        return "ANT-MAN AI: Mock response generated for test."
    
    monkeypatch.setattr("app.routers.message.chat", mock_chat)
    
    response = await client.post(
        f"/api/conversation/{conversation_id}/message",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"content": "How do I define a Pydantic V2 validator?"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["role"] == "assistant"
    assert data["content"] == "ANT-MAN AI: Mock response generated for test."


@pytest.mark.asyncio
async def test_create_message_nonexistent_conversation(client: AsyncClient, access_token: str):
    """Test posting message to non-existent conversation returns 404."""
    random_id = str(uuid.uuid4())
    response = await client.post(
        f"/api/conversation/{random_id}/message",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"content": "Hello in the void."},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Conversation not found"
