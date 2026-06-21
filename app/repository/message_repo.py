from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.conversation_model import Conversation
from ..models.messages_model import Message


class MessageRepository:

    async def get_conversation(
        self,
        db: AsyncSession,
        conversation_id: UUID,
        user_id,
    ):
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def create_message(
        self,
        db: AsyncSession,
        conversation_id: UUID,
        role: str,
        content: str,
    ):

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )

        db.add(message)
        await db.commit()
        await db.refresh(message)

        return message

    async def get_recent_messages(
        self,
        db: AsyncSession,
        conversation_id: UUID,
        limit: int = 20,
    ):

        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
        )

        messages = result.scalars().all()

        messages.reverse()

        return messages