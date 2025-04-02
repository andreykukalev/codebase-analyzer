from state.code_analysis import CodeAnalysisState
from utils.codebase_analyzer import CodebaseAnalyzer
from utils.graph_builder import GraphBuilder
from typing import Dict, Any

class ExtractNode:
    """A node that extracts classes and methods leveraging Abstract Syntax Tree (AST) parsers."""
    
    def __call__(self, state: CodeAnalysisState) -> Dict[str, Any]:
        print(f"Running extracting node...")

        traces_dir_path = state["traces_local_dir_path"] / "extracting_output"

        codebase_analyzer = CodebaseAnalyzer()
        codebase_analyzer.analyze_directory(state["codebase_local_dir_path"])
        codebase_analyzer.write_trees_to_files(traces_dir_path)

        graph_builder = GraphBuilder()
        graph_builder.build_methods_graph(codebase_analyzer.file_trees, codebase_analyzer.classes)
        graph_builder.write_graph_to_file(traces_dir_path)

        return {"methods_graph": graph_builder.graph, "classes_info": codebase_analyzer.classes}