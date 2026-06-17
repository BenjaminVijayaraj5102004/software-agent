import asyncio
from app.db.database import Base, engine
from app.models.users_model import User
from app.models.conversation_model import Conversation
from app.models.messages_model import Message
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers.authentication import router as authentication
from app.routers.token import router as Token


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield



app = FastAPI(lifespan=lifespan)

app.include_router(authentication)
app.include_router(Token)

