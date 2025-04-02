import ast
from typing import Dict
import networkx as nx
from networkx import DiGraph
from pathlib import Path
import os

class GraphBuilder:
    def __init__(self):
        self.graph = nx.DiGraph()

    def build_methods_graph(self, ast_trees: Dict[str, Dict], class_info: Dict[str, Dict]) -> None:
        """Builds a DiGraph representing method relationships from AST trees."""
        
        self.graph.clear()

        # Map to store method nodes for later edge creation
        method_nodes = {}
        labels = list(ast_trees.keys())
        trees = list(ast_trees.values())

        # Step 1: Add method nodes with attributes
        for tree, label in zip(trees, labels):
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_key = f"{label}:{node.name}"
                    if class_key in class_info:
                        class_data = class_info[class_key]
                        for method in class_data['methods']:
                            method_id = f"{class_key}:{method['name']}"
                            method_nodes[method['name']] = method_id  # Store for call lookups
                            self.graph.add_node(method_id, 
                                                label="Method",
                                                name=method['name'],
                                                class_name=node.name,
                                                file=label,
                                                args=[f"{arg['name']}:{arg['type'] or 'Any'}" for arg in method['args']],
                                                return_type=method['return_type'] or 'None',
                                                docstring=method['docstring'],
                                                calls=method['calls'])

        # Step 2: Add edges for method calls
        for node in self.graph.nodes:
            calls = self.graph.nodes[node].get('calls', [])
            for call in calls:
                # Try to find the called method in the graph
                for target_node in self.graph.nodes:
                    if (self.graph.nodes[target_node]['name'] == call and 
                        target_node != node):  # Avoid self-loops
                        self.graph.add_edge(node, target_node, type="call")

        # Step 3: Add edges for inheritance (if method overrides a base method)
        for class_key, class_data in class_info.items():
            file_path = class_data['file']
            class_name = class_data['name']
            for base in class_data['bases']:
                base_key = None
                for key, info in class_info.items():
                    if info['name'] == base and info['file'] != file_path:
                        base_key = key
                        break
                if base_key:
                    for method in class_data['methods']:
                        method_id = f"{class_key}:{method['name']}"
                        for base_method in class_info[base_key]['methods']:
                            if base_method['name'] == method['name']:
                                base_method_id = f"{base_key}:{base_method['name']}"
                                if method_id in self.graph and base_method_id in self.graph:
                                    self.graph.add_edge(method_id, base_method_id, type="overrides")

    def write_graph_to_file(self, output_dir: Path) -> None:
        """Writes the method graph to a DOT file."""

        if not self.graph.nodes:
            print("No graph to write")
            return

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        output_file = output_dir / "methods_graph.dot"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("digraph MethodGraph {\n")
            for node in self.graph.nodes:
                attrs = self.graph.nodes[node]
                label_str = (f"{attrs['name']} ({attrs['class_name']})\n"
                            f"Args: {', '.join(attrs['args'])}\n"
                            f"Returns: {attrs['return_type']}")
                f.write(f"    \"{node}\" [label=\"{label_str}\", shape=box];\n")
            for u, v, data in self.graph.edges(data=True):
                edge_style = " [style=\"dashed\"]" if data.get('type') == 'call' else " [style=\"dotted\"]"
                f.write(f"    \"{u}\" -> \"{v}\"{edge_style};\n")
            f.write("}\n")
        print(f"Method graph written to {output_file}")

    @staticmethod
    def serialize_graph_to_string(graph: DiGraph) -> str:
        """Serializes the method graph to a string for LLM input."""
        
        if not graph.nodes:
            return "Method Graph: Empty"

        lines = ["Method Graph:"]
        for node in graph.nodes:
            attrs = graph.nodes[node]
            node_str = (f"- {node} (name: {attrs['name']}, class: {attrs['class_name']}, "
                    f"file: {attrs['file']}, args: {', '.join(attrs['args'])}, "
                    f"returns: {attrs['return_type']})")
            lines.append(node_str)
                
            # Add outgoing edges
            edges = graph.out_edges(node, data=True)
            call_targets = [f"{v}" for u, v, d in edges if d.get('type') == 'call']
            if call_targets:
                lines.append(f"  -> calls: {', '.join(call_targets)}")
            override_targets = [f"{v}" for u, v, d in edges if d.get('type') == 'overrides']
            if override_targets:
                lines.append(f"  -> overrides: {', '.join(override_targets)}")
            
        return "\n".join(lines)
    