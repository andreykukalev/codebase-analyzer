import ast
import logging
from pathlib import Path
from typing import Dict
from networkx import DiGraph

logger = logging.getLogger(__name__)


class GraphBuilder:
    """Builds a directed graph (DiGraph) representing method relationships."""

    def __init__(self):
        self.graph = DiGraph()

    def build_methods_graph(self, ast_trees: Dict[str, Dict], class_info: Dict[str, Dict]) -> None:
        """
        Builds a DiGraph representing method relationships from AST trees.

        Args:
            ast_trees (Dict[str, Dict]): AST trees for the analyzed files.
            class_info (Dict[str, Dict]): Information about classes and methods.
        """
        self.graph.clear()

        # Map to store method nodes for later edge creation
        method_name_to_node = {}
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
                            method_name_to_node[method['name']] = method_id  # Store for call lookups
                            self.graph.add_node(
                                method_id,
                                label="Method",
                                name=method['name'],
                                class_name=node.name,
                                file=label,
                                args=[
                                    f"{arg['name']}:{arg['type'] or 'Any'}"
                                    for arg in method.get('args', [])
                                ],
                                return_type=method.get('return_type', 'None'),
                                docstring=method.get('docstring', ''),
                                calls=method.get('calls', []),
                            )

        # Step 2: Add edges for method calls
        for node in self.graph.nodes:
            calls = self.graph.nodes[node].get('calls', [])
            for call in calls:
                target_node = method_name_to_node.get(call)
                if target_node and target_node != node:  # Avoid self-loops
                    self._add_edge(node, target_node, "call")

        # Step 3: Add edges for inheritance (if method overrides a base method)
        for class_key, class_data in class_info.items():
            file_path = class_data['file']
            for base in class_data['bases']:
                base_key = next(
                    (key for key, info in class_info.items()
                     if info['name'] == base and info['file'] != file_path),
                    None
                )
                if base_key:
                    for method in class_data['methods']:
                        method_id = f"{class_key}:{method['name']}"
                        for base_method in class_info[base_key]['methods']:
                            if base_method['name'] == method['name']:
                                base_method_id = f"{base_key}:{base_method['name']}"
                                self._add_edge(method_id, base_method_id, "overrides")

    def _add_edge(self, source: str, target: str, edge_type: str) -> None:
        """
        Helper to add an edge to the graph.

        Args:
            source (str): Source node ID.
            target (str): Target node ID.
            edge_type (str): Type of the edge (e.g., "call", "overrides").
        """
        if source in self.graph and target in self.graph:
            self.graph.add_edge(source, target, type=edge_type)

    def write_graph_to_file(self, output_dir: Path) -> None:
        """
        Writes the method graph to a DOT file.

        Args:
            output_dir (Path): Directory where the DOT file will be saved.
        """
        if not self.graph.nodes:
            logger.warning("No graph to write")
            return

        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "methods_graph.dot"

        with open(output_file, 'w', encoding='utf-8') as output_file:
            output_file.write("digraph MethodGraph {\n")
            for node in self.graph.nodes:
                attrs = self.graph.nodes[node]
                label_str = (
                    f"{attrs['name']} ({attrs['class_name']})\n"
                    f"Args: {', '.join(attrs.get('args', []))}\n"
                    f"Returns: {attrs.get('return_type', 'None')}"
                )
                output_file.write(f"    \"{node}\" [label=\"{label_str}\", shape=box];\n")
            for u, v, data in self.graph.edges(data=True):
                edge_style = " [style=\"dashed\"]" if data.get('type') == 'call' else " [style=\"dotted\"]"
                output_file.write(f"    \"{u}\" -> \"{v}\"{edge_style};\n")
            output_file.write("}\n")
        logger.info(f"Method graph written to {output_file}")

    @staticmethod
    def serialize_graph_to_string(graph: DiGraph) -> str:
        """
        Serializes the method graph to a string for LLM input.

        Args:
            graph (DiGraph): The method graph to serialize.

        Returns:
            str: A string representation of the graph.
        """
        if not graph.nodes:
            return "Method Graph: Empty"

        lines = ["Method Graph:"]
        for node in graph.nodes:
            attrs = graph.nodes[node]
            node_str = (
                f"- {node} (name: {attrs['name']}, class: {attrs['class_name']}, "
                f"file: {attrs['file']}, args: {', '.join(attrs.get('args', []))}, "
                f"returns: {attrs.get('return_type', 'None')})"
            )
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