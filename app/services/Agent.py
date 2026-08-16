from langchain.messages import HumanMessage, AIMessage
from engineeringstack import EngineeringStack



llm = "ollama:qwen2.5-coder:7b "


agent = EngineeringStack(model = llm)


def chat(conversation_history, conversation_id: str | None = None):
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