import networkx as nx
from state import State
from utils.clients import OpenAIClient
from typing import Dict, Any

class AnalyzerNode:
    """A node that analyses collected classes and methods leveraging LLM"""

    def analyze_with_llm(self, method_graph: nx.DiGraph) -> Dict[str, Any]:
        """Uses an LLM to extract business logic from the method graph."""
        prompt = """
        You are an expert software analyst. Given the following method invocation graph, extract and summarize the business logic and functional requirements.
        
        Graph Data:
        {graph_data}
        
        Identify:
        - Key functionalities provided by the codebase
        - Main business processes implemented in the functions
        - Dependencies and relationships between functions
        - Any inferred high-level business requirements
        """
        
        graph_data = "\n".join([f"{src} -> {dst}" for src, dst in method_graph.edges()])
        full_prompt = prompt.format(graph_data=graph_data)
        
        return self.llm.invoke(full_prompt)

    def __init__(self, llm: OpenAIClient) -> None:
        self.llm = llm
    
    def __call__(self, state: State):
        llm_response = self.analyze_with_llm(state["methods_graph"])
        with open("C:\\_DATA\\VSCode\\codebase-analyzer\\src\\report\\temp.md", "w", encoding="utf-8") as file:
            file.write(llm_response.content)
            
        return {"llm_analysis_result": llm_response}
    




