import pytest


@pytest.mark.asyncio
async def test_login(client):
    response = await client.post(
        "/register",
        json={ 
            "email": "test2@gmail.com",
            "password": "test22004"
        }
    )

   




