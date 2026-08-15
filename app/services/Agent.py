from langchain.messages import HumanMessage, AIMessage


llm = "ollama:qwen3-coder:30b"
_agent = None


def _patch_middleware_deduplication():
    """Ensure deepagents and langchain factory handle duplicate middleware names gracefully."""
    try:
        import deepagents.graph
        import langchain.agents.factory

        orig_create_agent = langchain.agents.factory.create_agent

        def _dedup_create_agent(*args, **kwargs):
            if "middleware" in kwargs and kwargs["middleware"]:
                seen = set()
                deduped = []
                for m in kwargs["middleware"]:
                    name = getattr(m, "name", type(m).__name__)
                    if name not in seen:
                        seen.add(name)
                        deduped.append(m)
                kwargs["middleware"] = deduped
            return orig_create_agent(*args, **kwargs)

        deepagents.graph.create_agent = _dedup_create_agent
        langchain.agents.factory.create_agent = _dedup_create_agent
    except Exception:
        pass


def get_agent():
    global _agent
    if _agent is None:
        try:
            _patch_middleware_deduplication()
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