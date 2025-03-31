import os
from langchain_openai import ChatOpenAI

class OpenAIClient:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ChatOpenAI(
                model=os.getenv("MODEL_NAME"), 
                api_key=os.getenv("API_KEY"),
                base_url=os.getenv("BASE_URL"),
                temperature=float(os.getenv("TEMPERATURE", 0)))
            
        return cls._instance