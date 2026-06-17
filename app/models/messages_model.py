import uuid

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False
    )

    role = Column(String(20), nullable=False)

    content = Column(Text, nullable=False)

    token_count = Column(Integer)

    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index(
            "idx_messages_conversation_created",
            "conversation_id",
            "created_at"
        ),
    )