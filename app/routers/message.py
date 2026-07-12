from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..Agents.main import chat
from ..core.security import CurrentUser
from ..db.database import get_db
from ..repository.message_repo import MessageRepository
from ..schema.message_schema import  MessageCreate,MessageResponse


router = APIRouter(tags=["Message"])

message_repo = MessageRepository()


@router.post(
    "/api/conversation/{conversation_id}/message",
    response_model=MessageResponse,
)
async def create_message(
    conversation_id: UUID,
    message: MessageCreate,
    current: CurrentUser,
    db: AsyncSession = Depends(get_db),
):

    conversation = await message_repo.get_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=current.id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )


    await message_repo.create_message(
        db=db,
        conversation_id=conversation_id,
        role="user",
        content=message.content,
    )

   
    history = await message_repo.get_recent_messages(
        db=db,
        conversation_id=conversation_id,
        limit=20,
    )

    user_name = getattr(current, "name", None)

    ai_response = await chat(
        conversation_history=history,
        user_name=user_name,
    )

    assistant_message = await message_repo.create_message(
        db=db,
        conversation_id=conversation_id,
        role="assistant",
        content=ai_response,
    )

    return assistant_message