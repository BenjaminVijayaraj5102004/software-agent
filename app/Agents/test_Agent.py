from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage , AIMessage , SystemMessage

from ..core.config import settings


model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=settings.GOOGLE_API_KEY,
)

async def chat(conversation_history: list,user_name: str | None = None) -> str:

    system_prompt = "You are a helpful AI assistant."

    if user_name:
        system_prompt += (
            f" The user's name is {user_name}. "
            "Use their name naturally when appropriate."
        )

    messages = [SystemMessage(content=system_prompt)]

    for msg in conversation_history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        else:
            messages.append(AIMessage(content=msg.content))


    response = await model.ainvoke(messages)

    return response.content



