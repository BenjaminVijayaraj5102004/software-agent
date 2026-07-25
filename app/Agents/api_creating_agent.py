import asyncio
from langgraph.prebuilt import create_react_agent
from deepagents import create_deep_agent, CompiledSubAgent
from .model import chat_ollama
from .tools import get_filtered_tools
from ..core.config import settings

app = None

async def init_agent():
    """Initializes the nested agent architecture and compiles the final graph."""
    global app

  
    my_tools = await get_filtered_tools()

    rest_agent = create_react_agent(
        model=chat_ollama,
        tools=my_tools,
        name="REST_AGENT",
        prompt="""You are a REST API implementation agent.
        Never write FastAPI code from your own knowledge.
        If the request requires creating or modifying code, ALWAYS use one of your available tools.
        Only respond directly after all required tools have been executed."""
    )

    graphql_agent = create_react_agent(
        model=chat_ollama,
        tools=my_tools,
        name="GRAPHQL_AGENT",
        prompt="""You are a GraphQL API implementation agent.
        Never write FastAPI code from your own knowledge.
        If the request requires creating or modifying code, ALWAYS use one of your available tools.
        Only respond directly after all required tools have been executed."""
    )

    grpc_agent = create_react_agent(
        model=chat_ollama,
        tools=my_tools,
        name="gRPC_AGENT",
        prompt="""You are a gRPC API implementation agent.
        Never write FastAPI code from your own knowledge.
        If the request requires creating or modifying code, ALWAYS use one of your available tools.
        Only respond directly after all required tools have been executed."""
    )

  
    api_subagents = [
        CompiledSubAgent(
            name="rest-agent",
            description="Handles REST API implementation requests.",
            runnable=rest_agent
        ),
        CompiledSubAgent(
            name="graphql-agent",
            description="Handles GraphQL API implementation requests.",
            runnable=graphql_agent
        ),
        CompiledSubAgent(
            name="grpc-agent",
            description="Handles gRPC API implementation requests.",
            runnable=grpc_agent
        ),
    ]

    api_supervisor_graph = create_deep_agent(
        model=chat_ollama,
        subagents=api_subagents,
        system_prompt="""You are an API endpoint supervisor.
        Your job is to coordinate and delegate the user's request to the correct subagent using your task tool."""
    )

    
    main_subagents = [
        CompiledSubAgent(
            name="api-creator-supervisor",
            description="Use this agent to create, manage, or implement any API endpoints (REST, GraphQL, gRPC).",
            runnable=api_supervisor_graph
        )
    ]


    main_supervisor = create_deep_agent(
        subagents=main_subagents,
        model=chat_ollama,
        system_prompt="""Your role is to send information to subagents, get back the answer, and send it to the user.
        Workflow: user input -> main_supervisor -> api-creator-supervisor -> user output""",
        
    )

    return main_supervisor