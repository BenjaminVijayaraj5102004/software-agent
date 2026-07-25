import asyncio
from langchain.messages import HumanMessage, AIMessage
from . import api_creating_agent
from . import databaseagent
from .model import chat_ollama
from deepagents import create_deep_agent, CompiledSubAgent
app = None



async def init_agent():
    global app

    database_agent, api_agent = await asyncio.gather(
        databaseagent.init_agent(),
        api_creating_agent.init_agent(),
    )

    app = create_deep_agent(
        model=chat_ollama,
        subagents=[
            CompiledSubAgent(
                name="database-supervisor",
                description="Handles database-related tasks.",
                runnable=database_agent,
            ),
            CompiledSubAgent(
                name="api-supervisor",
                description="Handles API-related tasks.",
                runnable=api_agent,
            ),
        ],
        system_prompt="""
        Delegate database work to database-supervisor.
        Delegate API work to api-supervisor.
        """,
    )


async def chat(conversation_history: list, user_name = str | None) -> str:
    global app
    if app is None:
        raise RuntimeError("Agent graph not initialized. Call init_agent() first.")

    messages = []
    for msg in conversation_history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        else:
            messages.append(AIMessage(content=msg.content))

   

    response = await app.ainvoke(
        {"messages": messages},
    )

    return response["messages"][-1].content