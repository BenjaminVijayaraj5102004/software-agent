import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from main import app
from app.db.database import get_db, SessionLocal

async def override_get_db():
    async with SessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        yield client



@pytest_asyncio.fixture
async def test_login(client):
    response = await client.post(
        "/register",
        json={ 
            "email": "test2@gmail.com",
            "password": "test22004"
        }
    )


@pytest_asyncio.fixture
async def access_token(client: AsyncClient):

    response = await client.post(
        "/login/Token",
        data={
            "username": "test2@gmail.com",
            "password": "test22004",
        },
    )



   



@pytest_asyncio.fixture
async def conversation_id(client, access_token):
    response = await client.post(
        "/api/conversation/",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "title": "Test Conversation"
        }
    )


