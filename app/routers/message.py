from fastapi import APIRouter , Depends ,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..core.security import CurrentUser
from ..db.database import get_db
from ..models.messages_model import Message
from ..models.conversation_model import Conversation
from ..schema.message_schema import MessageCreate , MessageResponse
from ..Agents.test_Agent import chat
from uuid import UUID

router = APIRouter(
    tags=["message"]
)
@router.post(
    "/api/conversation/{conversation_id}/message",
    response_model=MessageResponse
)
async def create_message(
    conversation_id: UUID,
    message: MessageCreate,
    current: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current.id
        )
    )

    conversation = result.scalar_one_or_none()

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

  
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=message.content
    )

    db.add(user_message)
    await db.commit()


    ai_response = chat(message.content)


    assistant_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=ai_response
    )

    db.add(assistant_message)
    await db.commit()
    await db.refresh(assistant_message)

    return assistant_message