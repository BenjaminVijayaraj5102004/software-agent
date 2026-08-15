import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient):
    """Test user registration endpoint with valid @gmail.com email."""
    unique_email = f"user_{uuid.uuid4().hex[:6]}@gmail.com"
    response = await client.post(
        "/auth/register",
        json={
            "email": unique_email,
            "password": "validpassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["email"] == unique_email


@pytest.mark.asyncio
async def test_register_user_rejects_non_gmail(client: AsyncClient):
    """Test user registration endpoint rejects non-@gmail.com emails with 422."""
    response = await client.post(
        "/auth/register",
        json={
            "email": "invalid_domain@outlook.com",
            "password": "validpassword123",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_user_rejects_short_password(client: AsyncClient):
    """Test user registration endpoint rejects password shorter than 8 characters."""
    response = await client.post(
        "/auth/register",
        json={
            "email": f"short_pass_{uuid.uuid4().hex[:6]}@gmail.com",
            "password": "short",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_oauth2_success(client: AsyncClient, test_user):
    """Test OAuth2 password login returns valid JWT token."""
    response = await client.post(
        "/login/Token",
        data={
            "username": test_user["email"],
            "password": test_user["password"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_oauth2_invalid_password(client: AsyncClient, test_user):
    """Test OAuth2 login rejects incorrect password with 401."""
    response = await client.post(
        "/login/Token",
        data={
            "username": test_user["email"],
            "password": "wrong_password_here",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid password"


@pytest.mark.asyncio
async def test_login_oauth2_nonexistent_email(client: AsyncClient):
    """Test OAuth2 login rejects non-existent email with 401."""
    response = await client.post(
        "/login/Token",
        data={
            "username": "nonexistent_email@gmail.com",
            "password": "some_password",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email"


@pytest.mark.asyncio
async def test_me_endpoint(client: AsyncClient, access_token: str):
    """Test /me endpoint returns the bearer token."""
    response = await client.get(
        "/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert "token" in response.json()
