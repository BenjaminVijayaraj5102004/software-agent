from ..core.config import settings

from langchain_google_genai import ChatGoogleGenerativeAI




model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key = settings.GOOGLE_API_KEY
)

def chat(message : str):
    response =  model.invoke(message)
    print(type(response)) 
    return response.content



   