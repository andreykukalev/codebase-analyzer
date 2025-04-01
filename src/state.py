from pathlib import WindowsPath
import networkx as nx
from typing_extensions import TypedDict
from langchain_core.messages.ai import AIMessage

class State(TypedDict):
    codebase_local_path: WindowsPath
    llm_analysis_result: AIMessage   
    methods_graph: nx.DiGraph
    report_local_path: WindowsPath