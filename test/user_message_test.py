import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_create_message(client, access_token, conversation_id):
    response = await client.post(
        f"/api/conversation/{conversation_id}/message",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "content": "Explain FastAPI."
        }
    )