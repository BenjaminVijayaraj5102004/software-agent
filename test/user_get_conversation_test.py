import pytest

@pytest.mark.asyncio
async def test_get_conversation(client, access_token, conversation_id):
    response = await client.get(
        f"/api/conversation/{conversation_id}",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

  