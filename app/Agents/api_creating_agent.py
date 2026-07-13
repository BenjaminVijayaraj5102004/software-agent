from .model import MODEL, chat_ollama
from .tools import get_filtered_tools
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
import asyncio


api_endpoints = None

async def init_agent():
    global api_endpoints

    my_tools = await get_filtered_tools()

    rest_agent = create_react_agent(
        model=chat_ollama,
        tools=my_tools,
        name="REST_AGENT",
        prompt="""
        You are a REST API implementation agent.

        Never write FastAPI code from your own knowledge.

        If the request requires creating or modifying code, ALWAYS use one of your available tools.

        Only respond directly after all required tools have been executed.

        When finished, transfer back to the supervisor.
        """
    )

    graphl_agent = create_react_agent(
        model=chat_ollama,
        tools=my_tools,
        name="GRAPHQL_AGENT",
        prompt="""
        You are a GraphQL API implementation agent.

        Never write FastAPI code from your own knowledge.

        If the request requires creating or modifying code, ALWAYS use one of your available tools.

        Only respond directly after all required tools have been executed.

        When finished, transfer back to the supervisor.
        """
    )

    gRPC_agent = create_react_agent(
        model=chat_ollama,
        tools=my_tools,
        name="gRPC_AGENT",
        prompt="""
        You are a gRPC API implementation agent.

        Never write FastAPI code from your own knowledge.

        If the request requires creating or modifying code, ALWAYS use one of your available tools.

        Only respond directly after all required tools have been executed.

        When finished, transfer back to the supervisor.
        """
    )

    api_endpoints = create_supervisor(
        [rest_agent, graphl_agent, gRPC_agent],
        model=chat_ollama,
        prompt="""
        You are an API endpoint supervisor.
        Your ONLY job is to transfer the user's request to the correct agent.
        DO NOT answer the user directly.
        ALWAYS use the handoff tool.
        """
    ).compile()