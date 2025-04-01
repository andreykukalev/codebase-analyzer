from langchain_core.messages.ai import AIMessage
from networkx import DiGraph
from pathlib import Path
from typing_extensions import TypedDict

class CodeAnalysisState(TypedDict):
    codebase_local_path: Path
    llm_analysis_result: AIMessage   
    methods_graph: DiGraph
    report_local_path: Path