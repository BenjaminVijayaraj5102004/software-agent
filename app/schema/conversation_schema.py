from pydantic import BaseModel ,Field
from uuid import UUID


class ConversationCreate(BaseModel):
    title: str


class ConversationResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str = Field(
        min_length = 100,
        max_length = 500,
        description="Conversation title"
    )

    class Config:
        from_attributes = True