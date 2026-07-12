import asyncio

from langchain_protocol import Goto
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langchain.messages import HumanMessage, AIMessage
from ..core.config import settings
from .model import MODEL, chat_ollama
from .tools import get_filtered_tools
from . import api_creating_agent


async def chat(conversation_history: list , user_name: str | None = None) -> str:


    messages = []

    for msg in conversation_history:

        if msg.role == "user":
            messages.append(
                HumanMessage(content=msg.content)
            )

        else:
            messages.append(
                AIMessage(content=msg.content)
            )


    response = await api_creating_agent.api_endpoints.ainvoke(
        {
            "messages": messages
        }
    )


    return response["messages"][-1].content