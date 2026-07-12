import json
from langchain_ollama import ChatOllama
class MODEL():
    MODEL_NAME = "OLLAMA"

    def __init__(self, model, temp):
        self.model = model
        self.temp = temp

models = MODEL("qwen2.5-coder:7b", 0.7)



class PatchedOllama(ChatOllama):
    def invoke(self, *args, **kwargs):
        response = super().invoke(*args, **kwargs)
     
        if isinstance(response.content, str) and "transfer_to_rest_agent" in response.content:
            try:
             
                content = response.content.strip()
                if content.startswith("```json"):
                    content = content[7:-3].strip()
                data = json.loads(content)
                if data.get("name") == "transfer_to_rest_agent":
                    response.tool_calls = [{
                        "name": "transfer_to_rest_agent",
                        "args": data.get("arguments", {}),
                        "id": "call_patched_1"
                    }]
                    response.content = ""
            except Exception:
                pass
        return response

chat_ollama = PatchedOllama(model=models.model, temperature=models.temp)
