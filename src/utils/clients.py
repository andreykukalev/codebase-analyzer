import os
from langchain_openai import ChatOpenAI


class OpenAIClient:
    """
    A singleton client for interacting with OpenAI's Chat API.
    """

    _instance = None

    @classmethod
    def get_instance(cls) -> ChatOpenAI:
        """Get or create a singleton instance of the OpenAI client."""
        if cls._instance is None:
            cls._instance = ChatOpenAI(
                model=os.getenv("MODEL_NAME"),
                api_key=os.getenv("API_KEY"),
                base_url=os.getenv("BASE_URL"),
                temperature=float(os.getenv("TEMPERATURE", 0.3)),
            )
        return cls._instance