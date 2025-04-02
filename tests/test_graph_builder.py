import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
from src.utils.graph_builder import GraphBuilder

class TestGraphBuilder(unittest.TestCase):
    def setUp(self):
        """Set up a GraphBuilder instance for testing."""
        self.graph_builder = GraphBuilder()

    def test_build_methods_graph_creates_nodes(self):
        """Test that build_methods_graph correctly creates nodes."""
        ast_trees = {
            "file1.py": MagicMock(),
            "file2.py": MagicMock(),
        }
        class_info = {
            "file1.py:ClassA": {
                "methods": [
                    {"name": "method1", "args": [], "return_type": "int", "calls": []},
                    {"name": "method2", "args": [], "return_type": "str", "calls": []},
                ],
                "bases": [],
                "file": "file1.py",
            }
        }

        with patch("ast.walk", return_value=[MagicMock(name="ClassDef", __class__=MagicMock(name="ClassDef"))]):
            self.graph_builder.build_methods_graph(ast_trees, class_info)

        self.assertEqual(len(self.graph_builder.graph.nodes), 2)
        self.assertIn("file1.py:ClassA:method1", self.graph_builder.graph.nodes)
        self.assertIn("file1.py:ClassA:method2", self.graph_builder.graph.nodes)

    def test_build_methods_graph_creates_edges(self):
        """Test that build_methods_graph correctly creates edges for method calls."""
        ast_trees = {
            "file1.py": MagicMock(),
        }
        class_info = {
            "file1.py:ClassA": {
                "methods": [
                    {"name": "method1", "args": [], "return_type": "int", "calls": ["method2"]},
                    {"name": "method2", "args": [], "return_type": "str", "calls": []},
                ],
                "bases": [],
                "file": "file1.py",
            }
        }

        with patch("ast.walk", return_value=[MagicMock(name="ClassDef", __class__=MagicMock(name="ClassDef"))]):
            self.graph_builder.build_methods_graph(ast_trees, class_info)

        self.assertEqual(len(self.graph_builder.graph.edges), 1)
        self.assertIn(("file1.py:ClassA:method1", "file1.py:ClassA:method2"), self.graph_builder.graph.edges)

    def test_write_graph_to_file(self):
        """Test that write_graph_to_file writes the graph to a DOT file."""
        self.graph_builder.graph.add_node("method1", name="method1", class_name="ClassA", file="file1.py", args=[], return_type="int")
        self.graph_builder.graph.add_node("method2", name="method2", class_name="ClassA", file="file1.py", args=[], return_type="str")
        self.graph_builder.graph.add_edge("method1", "method2", type="call")

        with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
            with patch("pathlib.Path.mkdir") as mock_mkdir:  # Correctly mock the mkdir method
                output_dir = Path("test_output")
                self.graph_builder.write_graph_to_file(output_dir)

                mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
                mock_file.assert_called_once_with(output_dir / "methods_graph.dot", "w", encoding="utf-8")
                handle = mock_file()
                handle.write.assert_any_call("digraph MethodGraph {\n")
                handle.write.assert_any_call("    \"method1\" [label=\"method1 (ClassA)\nArgs: \nReturns: int\", shape=box];\n")
                handle.write.assert_any_call("    \"method1\" -> \"method2\" [style=\"dashed\"];\n")
                handle.write.assert_any_call("}\n")

    def test_serialize_graph_to_string(self):
        """Test that serialize_graph_to_string correctly serializes the graph."""
        self.graph_builder.graph.add_node("method1", name="method1", class_name="ClassA", file="file1.py", args=[], return_type="int")
        self.graph_builder.graph.add_node("method2", name="method2", class_name="ClassA", file="file1.py", args=[], return_type="str")
        self.graph_builder.graph.add_edge("method1", "method2", type="call")

        result = self.graph_builder.serialize_graph_to_string(self.graph_builder.graph)
        expected = (
            "Method Graph:\n"
            "- method1 (name: method1, class: ClassA, file: file1.py, args: , returns: int)\n"
            "  -> calls: method2\n"
            "- method2 (name: method2, class: ClassA, file: file1.py, args: , returns: str)"
        )
        self.assertEqual(result, expected)

    def test_serialize_graph_to_string_empty_graph(self):
        """Test that serialize_graph_to_string handles an empty graph."""
        result = self.graph_builder.serialize_graph_to_string(self.graph_builder.graph)
        self.assertEqual(result, "Method Graph: Empty")


if __name__ == "__main__":
    unittest.main()