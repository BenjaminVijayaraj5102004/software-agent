from fastapi import APIRouter ,Depends ,HTTPException
from ..schema.token import Token
from ..core.security import create_access_token,verfiy_password
from ..models.users_model import User
from ..db.database import get_db , Base , engine
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.security import oauth2_scheme
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
router = APIRouter()

@router.post("/login/Token" , response_model=Token )

async def check_authention(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
    
):
    result = (
       await db.execute(
        select(User).where(User.email == form_data.username)
        )
    )

    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email"
        )

    if not verfiy_password(
        form_data.password,
        db_user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    access_token = create_access_token(
        data={"sub": db_user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }




@router.get("/me")
def me(token: str = Depends(oauth2_scheme)):
    return {"token": token}