from typing import Literal
from pydantic import BaseModel
from uuid import UUID


class MessageCreate(BaseModel):
    role: Literal["user","assistant"]
    content: str 

class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    token_count: int | None = None
    
    model_config = {
        "from_attributes": True
    }


