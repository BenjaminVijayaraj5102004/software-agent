from fastapi import APIRouter ,Depends
from sqlalchemy.ext.asyncio import AsyncSession 
from ..schema.user_schema import UserCreate , UserResponse
from ..db.database import get_db , Base , engine
from ..models.users_model import User 

from ..core.config import settings 
from ..core.security import hash_password , verify_password



router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register" , response_model=UserResponse )
async def login_section (user: UserCreate , db : AsyncSession=Depends(get_db)):
    db_user =User(
        email = user.email,
        password_hash= hash_password(user.password)
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    
    return db_user