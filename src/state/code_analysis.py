from typing import Dict
from pathlib import Path
from typing_extensions import TypedDict
from networkx import DiGraph
from langchain_core.messages.ai import AIMessage


class CodeAnalysisState(TypedDict):
    """
    Represents the state of the code analysis process.

    Attributes:
        codebase_local_dir_path (Path): Path to the local codebase directory.
        traces_local_dir_path (Path): Path to the directory for trace files.
        report_local_file_path (Path): Path to the generated report file.
        llm_analysis_result (AIMessage): Results from the LLM analysis.
        classes_info (Dict): Information about extracted classes.
        methods_graph (DiGraph): Directed graph of method relationships.
    """
    codebase_local_dir_path: Path
    traces_local_dir_path: Path
    report_local_file_path: Path
    llm_analysis_result: AIMessage
    classes_info: Dict
    methods_graph: DiGraph