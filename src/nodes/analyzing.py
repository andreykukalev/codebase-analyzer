from networkx import DiGraph
from typing import Dict, Any
from state.code_analysis import CodeAnalysisState
from utils.clients import OpenAIClient
from utils.codebase_analyzer import CodebaseAnalyzer
from utils.graph_builder import GraphBuilder
from prompts.templates import extract_insights_prompt 
from utils.tools import Helper

class AnalyzeNode:
    """A node that analyses collected classes and methods leveraging LLM."""

    def _analyze_with_llm(self, digraph: DiGraph, classes: Dict) -> Dict[str, Any]:
        graph_data = GraphBuilder.serialize_graph_to_string(digraph)
        classes_data = CodebaseAnalyzer.serialize_classes_to_string(classes)
        
        full_prompt = extract_insights_prompt.format(method_graph=graph_data, classes_data=classes_data)
        
        return self.llm_client.invoke(full_prompt)

    def __init__(self, llm_client: OpenAIClient) -> None:
        self.llm_client = llm_client
    
    def __call__(self, state: CodeAnalysisState) -> Dict[str, Any]:
        print(f"Running analyzing node...")
        
        llm_response = self._analyze_with_llm(state["methods_graph"], state["classes_info"])

        Helper.write_to_file(
            state["traces_local_dir_path"] / "llm_analyze.txt", 
            llm_response.content)
        
        return {"llm_analysis_result": llm_response}
    




