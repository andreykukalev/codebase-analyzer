from state.code_analysis import CodeAnalysisState
from utils.codebase_analyzer import CodebaseAnalyzer
from utils.graph_builder import GraphBuilder

class ExtractNode:
    """A node that extracts classes and methods leveraging Abstract Syntax Tree (AST) parsers"""
    
    def __call__(self, state: CodeAnalysisState):
        codebase_analyzer = CodebaseAnalyzer()
        file_trees = codebase_analyzer.analyze_directory(state["codebase_local_path"])
        dependencies = codebase_analyzer.resolve_dependencies()

        graph_builder = GraphBuilder()
        graph_builder.build_combined_graph(file_trees, dependencies)

        return {"methods_graph": graph_builder.graph}