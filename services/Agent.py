from engineeringstack import create_engineering_stack
from langchain.messages import HumanMessage, AIMessage


llm = "ollama:qwen3-coder:30b"



agent = create_engineering_stack(model = llm)

def chat(conversation_history, user_name: str | None = None, conversation_id: str | None = None):
    messages = []

    for msg in conversation_history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        else:
            messages.append(AIMessage(content=msg.content))

    response = agent.invoke(
        {
            "messages": messages
        },
        thread_id=conversation_id
    )

    return response["final_answer"]