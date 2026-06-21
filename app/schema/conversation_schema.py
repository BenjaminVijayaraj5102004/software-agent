from pydantic import BaseModel ,Field   
from uuid import UUID
from datetime import datetime




class ConversationCreate(BaseModel):
    title: str


class ConversationResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str = Field(
        min_length = 1,
        max_length = 500,
        description="Conversation title"
    )

    model_config = {
        "from_attributes": True
    }


class ConversationListItem(BaseModel):
    id: UUID
    title: str
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
    