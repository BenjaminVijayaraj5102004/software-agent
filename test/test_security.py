import uuid
from datetime import timedelta
import pytest
from fastapi import HTTPException

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
    get_current_user,
)
from app.models.users_model import User


def test_password_hashing_and_verification():
    """Test password hashing produces distinct valid hashes and verifies correctly."""
    raw = "super_secure_pass_2026"
    hashed = hash_password(raw)
    
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_create_and_verify_access_token():
    """Test JWT token encoding and decoding."""
    email = "agent_developer@gmail.com"
    token = create_access_token(data={"sub": email})
    
    decoded_sub = verify_access_token(token)
    assert decoded_sub == email


def test_verify_access_token_invalid():
    """Test verify_access_token returns None for malformed tokens."""
    assert verify_access_token("invalid.jwt.token") is None
    assert verify_access_token("") is None


def test_create_access_token_custom_expiry():
    """Test JWT token creation with custom expiration."""
    email = "custom_exp@gmail.com"
    token = create_access_token(
        data={"sub": email},
        expires_delta=timedelta(hours=2)
    )
    assert verify_access_token(token) == email


@pytest.mark.asyncio
async def test_get_current_user_valid(db_session, test_user):
    """Test get_current_user resolves the authenticated User object from DB."""
    token = create_access_token(data={"sub": test_user["email"]})
    user = await get_current_user(token=token, db=db_session)
    
    assert user is not None
    assert user.email == test_user["email"]


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(db_session):
    """Test get_current_user raises 401 on invalid JWT."""
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token="invalid_token", db=db_session)
    assert excinfo.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_nonexistent_email(db_session):
    """Test get_current_user raises 401 when token subject does not exist in DB."""
    token = create_access_token(data={"sub": "ghost_user@gmail.com"})
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token, db=db_session)
    assert excinfo.value.status_code == 401
