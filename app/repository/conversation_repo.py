from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.conversation_model import Conversation
from uuid import UUID

class ConversationRepository:

    async def create_conversation(self,db: AsyncSession,title,user_id):
        conversation = Conversation(
            title=title,
            user_id=user_id
        )

        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

        return conversation

    async def get_conversations_list(self,db: AsyncSession,user_id):
        result = await db.execute(
            select(Conversation).where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        )

        return result.scalars().all()
    

    async def get_conversation_by_id(
            self,
            db : AsyncSession,
            conversation_id : UUID,
            user_id
    ):
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        )

        return result.scalar_one_or_none()
    
    async def delete_conversation_by_id(
        self,
        db: AsyncSession,
        conversation_id: UUID,
        user_id
    ):
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        )

        conversation = result.scalar_one_or_none()

        if conversation is None:
            return None

        await db.delete(conversation)
        await db.commit()

        return conversation



               