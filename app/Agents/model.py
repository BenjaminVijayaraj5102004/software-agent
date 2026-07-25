import json
from langchain_ollama import ChatOllama

class MODEL():
    MODEL_NAME = "OLLAMA"

    def __init__(self, model, temp):
        self.model = model
        self.temp = temp

models = MODEL("qwen2.5-coder:7b", 0)



class PatchedOllama(ChatOllama):
    tool_names: list = []

    def invoke(self, *args, **kwargs):
        response = super().invoke(*args, **kwargs)
     
        if isinstance(response.content, str) and any(tool in response.content for tool in self.tool_names):
            try:
             
                content = response.content.strip()
                if content.startswith("```json"):
                    content = content[7:-3].strip()
                data = json.loads(content)
                if data.get("name") in self.tool_names:
                    response.tool_calls = [{
                        "name": data.get("name"),
                        "args": data.get("arguments", {}),
                        "id": "call_patched_1"
                    }]
                    response.content = ""
            except Exception:
                pass
        return response

chat_ollama = PatchedOllama(
    model=models.model, 
    temperature=models.temp
)

