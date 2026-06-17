from datetime import UTC , datetime ,timedelta
from pydantic import SecretStr
from pwdlib import PasswordHash 
import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException ,status , Depends
from .config import settings
from sqlalchemy.orm import Session
from ..models.users_model import User
from jwt.exceptions import InvalidTokenError
from ..db.database import get_db
from typing import Annotated

password_hash =PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login/Token"
    )


def hash_password(password : str) -> str:
    return password_hash.hash(password)

def verfiy_password(plain_password : str , hash_password : str) -> bool:
    return password_hash.verify(plain_password , hash_password)


def create_access_token(data: dict , expires_delta : timedelta | None = None)-> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes= settings.access_token_expire_minutes,
        )
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY.get_secret_value(),
        algorithm=settings.algorithm,
    )
    return encoded_jwt

def verify_access_token(token : str )-> str | None:
    """Verify a JWT access token and return the subject (login.id) if vaalid"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY.get_secret_value(),
            algorithms=[settings.algorithm],
            options = {"require":["exp","sub"]},
        )
    except jwt.InvalidTokenError:
        return None
    else:
        return payload.get("sub")
    
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY.get_secret_value(),
            algorithms=[settings.algorithm]
        )

        email = payload.get("sub")

        if email is None:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    user = db.query(User.filter)(
        User.email == email
    ).first()

    if user is None:
        raise credentials_exception

    return user

Current_user = Annotated[User , Depends(get_current_user)]