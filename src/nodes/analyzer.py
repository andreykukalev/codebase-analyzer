from state import State
from utils.clients import OpenAIClient

class AnalyzerNode:
    """A node that analyses collected classes and methods leveraging LLM"""

    def __init__(self, llm: OpenAIClient) -> None:
        self.llm = llm
    
    def __call__(self, state: State):
        return {"messages": [""]}
    