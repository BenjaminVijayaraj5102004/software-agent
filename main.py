import asyncio
from app.db.database import Base, engine
from app.models.users_model import User
from app.models.conversation_model import Conversation
from app.models.messages_model import Message
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers.authentication import router as authentication
from app.routers.token import router as Token
from app.routers.conversation import router as conversation
from app.routers.message import router as Messages






app = FastAPI()



app.include_router(authentication)
app.include_router(Token)
app.include_router(conversation)
app.include_router(Messages)


