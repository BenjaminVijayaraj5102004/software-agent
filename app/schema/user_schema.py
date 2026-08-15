from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID


class UserCreate(BaseModel):
    email: EmailStr = Field(
        description="User email address (must be a @gmail.com address)",
        examples=["example@gmail.com"]
    )
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_gmail(cls, value: str) -> str:
        clean_email = str(value).strip().lower()
        if not clean_email.endswith("@gmail.com"):
            raise ValueError("Email must be a valid @gmail.com address (e.g. example@gmail.com)")
        return clean_email


class UserResponse(BaseModel):
    id: UUID
    email: str
    tier: str

    model_config = {
        "from_attributes": True
    }


