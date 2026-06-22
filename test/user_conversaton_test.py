import pytest


@pytest.mark.asyncio
async def test_create_conversation(client , access_token):
    response = await client.post(
        "/api/conversation/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "title": "Test Conversation"
        }
    )