import uuid
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from main import app
from app.db.database import get_db, SessionLocal
from app.core.security import hash_password
from app.models.users_model import User



async def override_get_db():
    async with SessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def db_session():
    """Direct database session fixture for repository / unit tests."""
    async with SessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client():
    """Async HTTP test client fixture for FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """Creates a unique test user in the database."""
    unique_id = uuid.uuid4().hex[:8]
    email = f"test_{unique_id}@gmail.com"
    raw_password = "testpassword123"
    
    user = User(
        email=email,
        password_hash=hash_password(raw_password),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return {"user": user, "email": email, "password": raw_password}


@pytest_asyncio.fixture
async def access_token(client: AsyncClient, test_user):
    """Obtains a valid JWT access token for the test user."""
    response = await client.post(
        "/login/Token",
        data={
            "username": test_user["email"],
            "password": test_user["password"],
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def conversation_id(client: AsyncClient, access_token: str):
    """Creates a test conversation and returns its UUID string."""
    response = await client.post(
        "/api/conversation/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"title": "Test Automated Conversation"},
    )
    assert response.status_code == 200
    return response.json()["id"]
