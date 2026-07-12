from fastapi import APIRouter ,Depends ,HTTPException , status
from sqlalchemy.ext.asyncio import AsyncSession 
from ..schema.user_schema import UserCreate , UserResponse
from ..db.database import get_db , Base , engine
from ..models.users_model import User 
from ..core.config import settings 
from ..core.security import hash_password , verify_password
from ..repository.userautentication_repo import userauthentication


user_repo = userauthentication()

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register" , response_model=UserResponse )
async def login_section (user: UserCreate , db : AsyncSession=Depends(get_db)):
    db_user = await user_repo.user_auth(
        db=db,
        email = user.email,
        password_hash = user.password
    )
    
    return db_user