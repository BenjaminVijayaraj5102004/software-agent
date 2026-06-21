from pydantic import BaseModel, EmailStr ,Field
from uuid import UUID


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length= 8 , max_length=128)


class UserResponse(BaseModel):
    id: UUID
    email: str
    tier: str

    model_config = {
        "from_attributes": True
    }


