import ast
from typing import Dict, Set
from networkx import DiGraph

class GraphBuilder:
    def __init__(self):
        self.graph = DiGraph()

    def build_graph_from_ast(self, tree: ast.AST, file_path: str) -> None:
        """Build a directed graph from a single AST structure."""
        def add_node_and_edges(node, parent_id=None):
            node_id = f"{type(node).__name__}_{id(node)}"
            node_label = type(node).__name__
            
            attributes = {'label': node_label, 'file': file_path}
            self.graph.add_node(node_id, **attributes)
            
            if parent_id:
                self.graph.add_edge(parent_id, node_id)
            
            for child in ast.iter_child_nodes(node):
                add_node_and_edges(child, node_id)
                
            if isinstance(node, ast.ClassDef):
                self.graph.nodes[node_id]['name'] = node.name
            elif isinstance(node, ast.FunctionDef):
                self.graph.nodes[node_id]['name'] = node.name
            elif isinstance(node, ast.Name):
                self.graph.nodes[node_id]['id'] = node.id

        if tree:
            add_node_and_edges(tree)

    def build_combined_graph(self, file_trees: Dict[str, ast.AST], 
                           dependencies: Dict[str, Set[str]]) -> None:
        """Build a single graph combining all ASTs with inter-file dependencies."""
        if not file_trees:
            print("No ASTs provided to build graph")
            return

        # Add a root node
        root_id = "Root"
        self.graph.add_node(root_id, label="ProjectRoot")

        # Build AST subgraphs for each file
        for file_path, tree in file_trees.items():
            module_id = f"Module_{id(tree)}"
            self.graph.add_node(module_id, label="Module", file=file_path)
            self.graph.add_edge(root_id, module_id)
            self.build_graph_from_ast(tree, file_path)
            tree_root_id = f"Module_{id(tree)}"
            if tree_root_id in self.graph.nodes:
                self.graph.add_edge(module_id, tree_root_id)

        # Add dependency edges between classes
        for class_key, deps in dependencies.items():
            class_node_id = None
            # Find the ClassDef node for this class
            for node in self.graph.nodes:
                if (self.graph.nodes[node].get('label') == 'ClassDef' and 
                    self.graph.nodes[node].get('file') == class_key.split(':')[0] and 
                    self.graph.nodes[node].get('name') == class_key.split(':')[1]):
                    class_node_id = node
                    break
            
            if class_node_id:
                for dep in deps:
                    dep_node_id = None
                    if ':' in dep:  # Fully qualified dependency (file:class)
                        dep_file, dep_class = dep.split(':')
                        for node in self.graph.nodes:
                            if (self.graph.nodes[node].get('label') == 'ClassDef' and 
                                self.graph.nodes[node].get('file') == dep_file and 
                                self.graph.nodes[node].get('name') == dep_class):
                                dep_node_id = node
                                break
                    if dep_node_id:
                        self.graph.add_edge(class_node_id, dep_node_id, type="dependency")