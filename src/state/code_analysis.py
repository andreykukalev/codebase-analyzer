from langchain_core.messages.ai import AIMessage
from networkx import DiGraph
from pathlib import Path
from typing import Dict, List
from typing_extensions import TypedDict

class CodeAnalysisState(TypedDict):
    codebase_local_dir_path: Path
    traces_local_dir_path: Path
    report_local_file_path: Path
    llm_analysis_result: AIMessage 
    classes_info: Dict
    methods_graph: DiGraph
    