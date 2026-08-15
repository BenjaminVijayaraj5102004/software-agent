import uuid
import pytest
from app.repository.userautentication_repo import userauthentication
from app.repository.conversation_repo import ConversationRepository
from app.repository.message_repo import MessageRepository
from app.core.security import verify_password


@pytest.mark.asyncio
async def test_user_authentication_repo_creation(db_session):
    """Test user repository saves user with securely hashed password."""
    repo = userauthentication()
    unique_email = f"repo_test_{uuid.uuid4().hex[:6]}@gmail.com"
    raw_pass = "repo_password_123"
    
    user = await repo.user_auth(
        db=db_session,
        email=unique_email,
        password_hash=raw_pass,
    )
    
    assert user.id is not None
    assert user.email == unique_email
    assert verify_password(raw_pass, user.password_hash) is True


@pytest.mark.asyncio
async def test_conversation_repo_crud(db_session, test_user):
    """Test ConversationRepository create, get list, get by ID, and delete."""
    repo = ConversationRepository()
    user_id = test_user["user"].id
    
    # Create
    conv = await repo.create_conversation(
        db=db_session,
        title="Repo Test Conversation",
        user_id=user_id
    )
    assert conv.id is not None
    assert conv.title == "Repo Test Conversation"
    assert conv.user_id == user_id
    
    # Get by ID
    fetched = await repo.get_conversation_by_id(
        db=db_session,
        conversation_id=conv.id,
        user_id=user_id
    )
    assert fetched is not None
    assert fetched.id == conv.id
    
    # Get list
    conv_list = await repo.get_conversations_list(
        db=db_session,
        user_id=user_id
    )
    assert len(conv_list) >= 1
    assert any(c.id == conv.id for c in conv_list)
    
    # Delete
    deleted = await repo.delete_conversation_by_id(
        db=db_session,
        conversation_id=conv.id,
        user_id=user_id
    )
    assert deleted is not None
    assert deleted.id == conv.id
    
    # Verify deletion
    after_del = await repo.get_conversation_by_id(
        db=db_session,
        conversation_id=conv.id,
        user_id=user_id
    )
    assert after_del is None


@pytest.mark.asyncio
async def test_message_repo_creation_and_history(db_session, test_user):
    """Test MessageRepository creates messages and retrieves history in correct order."""
    conv_repo = ConversationRepository()
    msg_repo = MessageRepository()
    user_id = test_user["user"].id
    
    conv = await conv_repo.create_conversation(
        db=db_session,
        title="Message History Conversation",
        user_id=user_id
    )
    
    # Create user message
    msg1 = await msg_repo.create_message(
        db=db_session,
        conversation_id=conv.id,
        role="user",
        content="Hello Ant-Man Agent",
    )
    assert msg1.id is not None
    assert msg1.role == "user"
    assert msg1.content == "Hello Ant-Man Agent"
    
    # Create assistant message
    msg2 = await msg_repo.create_message(
        db=db_session,
        conversation_id=conv.id,
        role="assistant",
        content="Hello! How can I assist you with code today?",
    )
    assert msg2.id is not None
    assert msg2.role == "assistant"
    
    # Retrieve history
    history = await msg_repo.get_recent_messages(
        db=db_session,
        conversation_id=conv.id,
        limit=10
    )
    assert len(history) == 2
    assert history[0].content == "Hello Ant-Man Agent"
    assert history[1].content == "Hello! How can I assist you with code today?"
