from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain.messages import HumanMessage, AIMessage
from ..core.config import settings
from ..Mcp.server import system_prompt
from ..Mcp.client import get_tools


model = ChatOllama(
    model="qwen3.5:9b",
    temperature=0,
)

async def get_agent():

    tools = await get_tools()

    agent = create_react_agent(
        model=model,
        tools=tools,
        prompt=system_prompt()
    )

    return agent


async def chat(conversation_history: list , user_name: str | None = None) -> str:

    agent = await get_agent()

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


    response = await agent.ainvoke(
        {
            "messages": messages
        }
    )


    return response["messages"][-1].content