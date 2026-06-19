from uuid import UUID
from fastapi import APIRouter, Depends ,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..Agents.test_Agent import chat
from ..db.database import get_db
from ..models.conversation_model import Conversation
from ..schema.conversation_schema import (
    ConversationCreate,
    ConversationResponse
)
from ..core.security import CurrentUser

router = APIRouter(
    tags=["Conversation"]
)


@router.post(
    "/api/conversation/",
    response_model=ConversationResponse,
   
)
async def create_conversation(
    conversation: ConversationCreate,
    currents : CurrentUser,
    db: AsyncSession = Depends(get_db)
  
    
):
    
    db_conversation = Conversation(
        title= conversation.title,
        user_id = currents.id
    )
    db.add(db_conversation)
    await db.commit()
    await db.refresh(db_conversation)
    return db_conversation


@router.get(
    "/api/conversation",
    response_model=list[ConversationResponse]
)
async def get_conversations(
    currents: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == currents.id)
        .order_by(Conversation.updated_at.desc())
    )

    return result.scalars().all()

@router.get(
    "/api/conversation/{conversation_id}",
    response_model=ConversationResponse
)
async def get_conversation(
    conversation_id: UUID,
    currents: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == currents.id
        )
    )

    conversation = result.scalar_one_or_none()

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    return conversation

@router.delete("/api/conversation/{conversation_id}")
async def delete_conversation(
    conversation_id: UUID,
    currents: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == currents.id
        )
    )

    conversation = result.scalar_one_or_none()

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    await db.delete(conversation)
    await db.commit()

    return {
        "message": "Conversation deleted successfully"
    }