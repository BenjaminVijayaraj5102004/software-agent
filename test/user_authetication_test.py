import pytest


@pytest.mark.asyncio
async def test_login(client):
    response = await client.post(
        "/register",
        json={ 
            "email": "test1@gmail.com",
            "password": "test12004"
        }
    )

   




