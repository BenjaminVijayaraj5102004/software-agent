from ..models.users_model import User
from ..db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr
from ..core.security import hash_password


class userauthentication:
    async def user_auth(self, db: AsyncSession, email: EmailStr, password_hash: str, name: str = None):
        db_user = User(
            email=email,
            password_hash=hash_password(password_hash)
        )

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        return db_user
    

