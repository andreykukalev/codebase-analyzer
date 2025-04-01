from networkx import DiGraph
from typing import Dict, Any
from state.code_analysis import CodeAnalysisState
from utils.clients import OpenAIClient

class AnalyzeNode:
    """A node that analyses collected classes and methods leveraging LLM"""

    @staticmethod
    def _serialize_graph_for_llm(graph: DiGraph) -> str:
        """Serialize graph data into a text format for LLM input."""
        output = ["Codebase Structure:"]
        
        # Extract classes and their details
        for node in graph.nodes:
            if graph.nodes[node]['label'] == 'ClassDef':
                class_name = graph.nodes[node].get('name', 'Unknown')
                file = graph.nodes[node].get('file', 'Unknown')
                output.append(f"Class: {class_name} (File: {file})")
                
                # Find methods (children with label 'FunctionDef')
                methods = []
                for neighbor in graph.neighbors(node):
                    if graph.nodes[neighbor]['label'] == 'FunctionDef':
                        method_name = graph.nodes[neighbor].get('name', 'Unknown')
                        # You could enhance this with args/return types from CodeAnalyzer
                        methods.append(method_name)
                if methods:
                    output.append(f"  Methods: {', '.join(methods)}")
        
        # Extract dependencies
        output.append("\nDependencies:")
        for u, v in graph.edges:
            if graph[u][v].get('type') == 'dependency':
                u_name = graph.nodes[u].get('name', 'Unknown')
                v_name = graph.nodes[v].get('name', 'Unknown')
                u_file = graph.nodes[u].get('file', 'Unknown')
                v_file = graph.nodes[v].get('file', 'Unknown')
                output.append(f"{u_name} ({u_file}) depends on {v_name} ({v_file})")
        
        return "\n".join(output)
        
    def _analyze_with_llm(self, digraph: DiGraph) -> Dict[str, Any]:
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
        
        graph_data = self._serialize_graph_for_llm(digraph)
        full_prompt = prompt.format(graph_data=graph_data)
        
        return self.llm_client.invoke(full_prompt)

    def __init__(self, llm_client: OpenAIClient) -> None:
        self.llm_client = llm_client
    
    def __call__(self, state: CodeAnalysisState):
        llm_response = self._analyze_with_llm(state["methods_graph"])            
        return {"llm_analysis_result": llm_response}
    




