import ast
import os
import networkx as nx
from state import State
from typing import Dict, Any

class ExtractNode:
    """A node that extracts classes and methods leveraging Abstract Syntax Tree (AST) parsers"""

    @staticmethod
    def extract_classes_and_methods(file_path: str) -> Dict[str, Any]:
        """Extract classes and methods from a given Python file using AST."""
        with open(file_path, "r", encoding="utf-8") as file:
            tree = ast.parse(file.read(), filename=file_path)
        
        extracted_data = {"classes": {}, "functions": {}}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                extracted_data["classes"][node.name] = {
                    "methods": {},
                    "type": "class"
                }
            elif isinstance(node, ast.FunctionDef):
                args = [arg.arg for arg in node.args.args]
                return_type = ast.unparse(node.returns) if node.returns else "None"
                extracted_data["functions"][node.name] = {
                    "args": args,
                    "return_type": return_type,
                    "type": "function",
                    "calls": []
                }
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Call) and isinstance(stmt.func, ast.Name):
                        extracted_data["functions"][node.name]["calls"].append(stmt.func.id)
        
        return extracted_data
    
    @staticmethod
    def analyze_codebase(root_dir: str) -> Dict[str, Any]:
        """Walk through the root directory and parse Python files."""
        codebase_data = {}
    
        for root, _, files in os.walk(root_dir):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    codebase_data[file_path] = ExtractNode.extract_classes_and_methods(file_path)

        return codebase_data

    @staticmethod
    def build_method_graph(codebase_data: Dict[str, Any]) -> nx.DiGraph:
        """Constructs a directed graph representing method relationships."""
        G = nx.DiGraph()
        
        for file, content in codebase_data.items():
            for class_name, class_data in content.get("classes", {}).items():
                G.add_node(class_name, type="class", file=file)
                for method_name in class_data["methods"]:
                    G.add_node(method_name, type="method", file=file)
                    G.add_edge(class_name, method_name)  # Link class to its methods
            
            for func_name, func_data in content.get("functions", {}).items():
                G.add_node(func_name, type="function", file=file, args=func_data["args"], return_type=func_data["return_type"])
                for called_func in func_data["calls"]:
                    if called_func in G.nodes:
                        G.add_edge(func_name, called_func)  # Link function to its calls
        
        return G
    
    def __init__(self) -> None:
        return None
    
    def __call__(self, state: State):
        codebase_data = self.analyze_codebase(state["codebase_local_path"])
        methods_graph = self.build_method_graph(codebase_data)
        return {"methods_graph": methods_graph}