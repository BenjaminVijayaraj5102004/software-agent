from uuid import UUID
from fastapi import APIRouter, Depends ,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..Agents.Frontend_Agent import chat
from ..db.database import get_db
from ..models.conversation_model import Conversation
from ..schema.conversation_schema import ConversationCreate,ConversationResponse
from ..core.security import CurrentUser
from ..repository.conversation_repo import ConversationRepository


router = APIRouter(
    tags=["Conversation"]
)


conversation_repo= ConversationRepository()


@router.post(
    "/api/conversation/",
    response_model=ConversationResponse,
   
)
async def create_conversation(
    conversation: ConversationCreate,
    currents : CurrentUser,
    db: AsyncSession = Depends(get_db)
  
    
):
    
    return await conversation_repo.create_conversation(
        db=db,
        title = conversation.title,
        user_id = currents.id
    )


@router.get(
    "/api/conversation",
    response_model=list[ConversationResponse]
)
async def get_conversations(
    currents: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    
    return await conversation_repo.get_conversations_list(
        db=db,
        user_id = currents.id
    )

@router.get(
    "/api/conversation/{conversation_id}",
    response_model=ConversationResponse
)
async def get_conversation(
    conversation_id: UUID,
    currents: CurrentUser,
    db: AsyncSession = Depends(get_db)
):

    conversation = await conversation_repo.get_conversation_by_id(
        db=db,
        conversation_id=conversation_id,
        user_id=currents.id
    )

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

    conversation = await conversation_repo.delete_conversation_by_id(
        db=db,
        conversation_id=conversation_id,
        user_id=currents.id
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    return {
        "message": "Conversation deleted successfully"
    }