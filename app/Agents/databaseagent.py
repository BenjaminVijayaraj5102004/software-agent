import asyncio
from platform import system
from typing import Annotated, TypedDict

from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.prebuilt import create_react_agent
from deepagents import create_deep_agent, CompiledSubAgent
from langchain.messages import HumanMessage, AIMessage
from .model import chat_ollama
from .tools import get_filtered_tools
from ..core.config import settings

app = None

async def init_agent():
    """Initializes the nested agent architecture and compiles the final graph."""
    global app

  
    my_tools = await get_filtered_tools()

    RDMS_AGENT = create_react_agent(
        model=chat_ollama,
        tools=my_tools,
        name="RDMS_AGENT",
        prompt="""You are a RDMS API implementation agent.
        Never write (mysql , postgres) code from your own knowledge.
        If the request requires creating or modifying code, ALWAYS use one of your available tools.
        Only respond directly after all required tools have been executed."""
    )

    NoSQL_AGENT = create_react_agent(
        model=chat_ollama,
        tools=my_tools,
        name="NoSQL_AGENT",
        prompt="""You are a NoSQL API implementation agent.
        Never write monogdb code from your own knowledge.
        If the request requires creating or modifying code, ALWAYS use one of your available tools.
        Only respond directly after all required tools have been executed."""
    )

    redis_agent = create_react_agent(
        model=chat_ollama,
        tools=my_tools,
        name="redis_AGENT",
        prompt="""You are a redis API implementation agent.
        Never write redis code from your own knowledge.
        If the request requires creating or modifying code, ALWAYS use one of your available tools.
        Only respond directly after all required tools have been executed."""
    )

  
    database_subagents = [
        CompiledSubAgent(
            name="RDMS_AGENT",
            description="Handles RDMS API implementation requests.",
            runnable=RDMS_AGENT
        ),
        CompiledSubAgent(
            name="NoSQL_AGENT",
            description="Handles NoSQL API implementation requests.",
            runnable=NoSQL_AGENT
        ),
        CompiledSubAgent(
            name ="Redis_AGENT",
            description="Handles Redis API implementation requests.",
            runnable=redis_agent
        )
    ]

    db_supervisor_graph = create_deep_agent(
        model=chat_ollama,
        subagents=database_subagents,
        system_prompt="""You are an API endpoint supervisor.
        Your job is to coordinate and delegate the user's request to the correct subagent using your task tool."""
    )

    
    main_subagents = [
        CompiledSubAgent(
            name="db-creator-supervisor",
            description="Use this agent to create, manage, or implement any API endpoints (REST, GraphQL, gRPC).",
            runnable=db_supervisor_graph
        )
    ]

   

    main_supervisor = create_deep_agent(
        subagents=main_subagents,
        model=chat_ollama,
        system_prompt="""Your role is to send information to subagents, get back the answer, and send it to the user.
        Workflow: user input -> main_supervisor -> DB-creator-supervisor -> user output""",
        
    )

    return main_supervisor