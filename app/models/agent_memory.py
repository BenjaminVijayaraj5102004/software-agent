import uuid
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.db.database import Base

class AgentMemory(Base):
    """
    Model for storing LangGraph agent conversational memory and metadata.
    """
    __tablename__ = "agent_memory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Optional link to user or conversation if you want to track it
    # user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    # conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=True)

    thread_id = Column(String(255), nullable=False, unique=True, index=True)
    state = Column(JSONB, nullable=True) # Postgres JSONB is great for states

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_agent_memory_thread", "thread_id"),
    )
