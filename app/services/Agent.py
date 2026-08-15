from langchain.messages import HumanMessage, AIMessage


llm = "ollama:qwen3-coder:30b"
_agent = None


def get_agent():
    global _agent
    if _agent is None:
        try:
            from engineeringstack import create_engineering_stack
            _agent = create_engineering_stack(model=llm)
        except ImportError as e:
            raise ImportError(
                "The 'engineeringstack' package is not installed in this Python environment. "
                "Please install it using 'pip install -e <path-to-engineering-stack>' or 'uv pip install -e ...'"
            ) from e
    return _agent


def chat(conversation_history, user_name: str | None = None, conversation_id: str | None = None):
    messages = []

    for msg in conversation_history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        else:
            messages.append(AIMessage(content=msg.content))

    agent = get_agent()
    response = agent.invoke(
        {
            "messages": messages
        },
        thread_id=conversation_id
    )

    return response["final_answer"]