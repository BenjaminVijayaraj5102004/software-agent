import uuid
import pytest
from pydantic import ValidationError

from app.schema.user_schema import UserCreate, UserResponse
from app.schema.conversation_schema import ConversationCreate, ConversationResponse
from app.schema.message_schema import MessageCreate, MessageResponse
from app.schema.token import Token


def test_user_create_valid_gmail():
    """Test UserCreate accepts standard @gmail.com addresses."""
    user = UserCreate(email="developer@gmail.com", password="securepassword123")
    assert user.email == "developer@gmail.com"
    assert user.password == "securepassword123"


def test_user_create_case_insensitive_and_whitespace_trim():
    """Test UserCreate strips whitespace and normalizes email domain."""
    user = UserCreate(email="  MyEmail@GMAIL.COM  ", password="securepassword123")
    assert user.email == "myemail@gmail.com"


def test_user_create_rejects_non_gmail():
    """Test UserCreate strictly rejects non-@gmail.com email addresses."""
    with pytest.raises(ValidationError) as excinfo:
        UserCreate(email="user@yahoo.com", password="securepassword123")
    assert "@gmail.com" in str(excinfo.value)


def test_user_create_rejects_short_password():
    """Test UserCreate rejects password shorter than 8 characters."""
    with pytest.raises(ValidationError) as excinfo:
        UserCreate(email="valid@gmail.com", password="short")
    assert "at least 8 characters" in str(excinfo.value) or "min_length" in str(excinfo.value)


def test_user_create_rejects_invalid_email_format():
    """Test UserCreate rejects completely invalid email formats."""
    with pytest.raises(ValidationError):
        UserCreate(email="notanemail", password="securepassword123")


def test_user_response_model():
    """Test UserResponse serialization and fields."""
    user_id = uuid.uuid4()
    resp = UserResponse(id=user_id, email="dev@gmail.com", tier="free")
    assert resp.id == user_id
    assert resp.email == "dev@gmail.com"
    assert resp.tier == "free"


def test_conversation_create_schema():
    """Test ConversationCreate schema."""
    conv = ConversationCreate(title="New AI Feature discussion")
    assert conv.title == "New AI Feature discussion"


def test_message_create_schema():
    """Test MessageCreate schema."""
    msg = MessageCreate(content="Explain FastAPI dependency injection.")
    assert msg.content == "Explain FastAPI dependency injection."


def test_token_schema():
    """Test Token schema structure."""
    token = Token(access_token="mock_jwt_token_123", token_type="bearer")
    assert token.access_token == "mock_jwt_token_123"
    assert token.token_type == "bearer"
