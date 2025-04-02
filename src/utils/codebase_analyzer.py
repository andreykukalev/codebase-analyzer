import ast
import os
from typing import Dict, List
from pathlib import Path


class CodebaseAnalyzer:
    """Analyzes Python codebases using AST to extract classes and methods."""

    def __init__(self):
        self.classes = {}
        self.file_trees = {}

    def analyze_file(self, file_path: str) -> ast.AST:
        """Analyze a single source code file using the AST parser."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                source = file.read()
                tree = ast.parse(source)
                self.file_trees[file_path] = tree
                self._extract_classes(tree, file_path)
                return tree
        except (FileNotFoundError, SyntaxError) as e:
            print(f"Error analyzing {file_path}: {str(e)}")
            return None

    def _extract_classes(self, tree: ast.AST, file_path: str) -> None:
        """Extract class definitions from the AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = self._extract_class_info(node, file_path)
                self.classes[f"{file_path}:{class_info['name']}"] = class_info

    def _extract_class_info(self, node: ast.ClassDef, file_path: str) -> Dict:
        """Extract information about a class."""
        class_info = {
            'name': node.name,
            'file': file_path,
            'line': node.lineno,
            'methods': [],
            'bases': [
                base.id if isinstance(base, ast.Name) else str(base)
                for base in node.bases
            ]
        }
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._extract_method_info(item)
                class_info['methods'].append(method_info)
        return class_info

    def _extract_method_info(self, node: ast.FunctionDef) -> Dict:
        """Extract method information, including arguments and return type."""
        args = []
        for arg in node.args.args:
            arg_type = None
            if arg.annotation:
                try:
                    arg_type = ast.unparse(arg.annotation)
                except Exception:
                    arg_type = None  # Fallback if unparse fails
            args.append({'name': arg.arg, 'type': arg_type})

        return_type = None
        if node.returns:
            try:
                return_type = ast.unparse(node.returns)
            except Exception:
                return_type = None  # Fallback if unparse fails

        return {
            'name': node.name,
            'line': node.lineno,
            'args': args,
            'return_type': return_type,
            'docstring': ast.get_docstring(node),
            'calls': self._extract_method_calls(node)
        }

    def _extract_method_calls(self, node: ast.FunctionDef) -> List[str]:
        """Extract method calls from a function definition."""
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)
        return calls

    def analyze_directory(self, directory: str) -> Dict[str, ast.AST]:
        """Scan a directory and analyze all Python files."""
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    self.analyze_file(os.path.join(root, file))
        return self.file_trees

    def write_trees_to_files(self, output_dir: Path) -> None:
        """Write AST trees and class data to files."""
        if not self.file_trees:
            print("No data available to write.")
            return

        os.makedirs(output_dir, exist_ok=True)

        classes_by_file = {}
        for key, class_info in self.classes.items():
            file_path = class_info['file']
            if file_path not in classes_by_file:
                classes_by_file[file_path] = []
            classes_by_file[file_path].append(class_info)

        for file_path in self.file_trees:
            base_name = os.path.basename(file_path).replace('.py', '')

            ast_output_file = os.path.join(output_dir, f"{base_name}_ast.txt")
            ast_text = ast.dump(self.file_trees[file_path], indent=2)
            with open(ast_output_file, 'w', encoding='utf-8') as output_file:
                output_file.write(ast_text)

            class_output_file = os.path.join(output_dir, f"{base_name}_classes.txt")
            with open(class_output_file, 'w', encoding='utf-8') as output_file:
                if file_path in classes_by_file:
                    for class_info in classes_by_file[file_path]:
                        output_file.write(f"Class: {class_info['name']}\n")
                        output_file.write(f"Line: {class_info['line']}\n")
                        if class_info['bases']:
                            output_file.write(f"Inherits from: {', '.join(class_info['bases'])}\n")
                        if class_info['methods']:
                            output_file.write("Methods:\n")
                            for method in class_info['methods']:
                                output_file.write(f"  {method['name']} (line {method['line']})\n")
                                if method['args']:
                                    args_str = ', '.join(
                                        f"{arg['name']}: {arg['type'] or 'Any'}"
                                        for arg in method['args']
                                    )
                                    output_file.write(f"    Args: {args_str}\n")
                                if method['return_type']:
                                    output_file.write(f"    Returns: {method['return_type']}\n")
                                if method['docstring']:
                                    output_file.write(f"    Docstring: {method['docstring']}\n")
                        output_file.write("\n")
                else:
                    output_file.write("No classes found in this file.\n")

    @staticmethod
    def serialize_classes_to_string(classes: Dict) -> str:
        """Serialize the dictionary of class info into a string."""
        if not classes:
            return "Classes: None"

        lines = ["Classes:"]
        for class_key, class_info in classes.items():
            class_str = (
                f"- {class_key} (name: {class_info['name']}, file: {class_info['file']}, "
                f"line: {class_info['line']})"
            )
            lines.append(class_str)
            if class_info['bases']:
                lines.append(f"  Inherits: {', '.join(class_info['bases'])}")
            if class_info['methods']:
                lines.append("  Methods:")
                for method in class_info['methods']:
                    method_str = (
                        f"    - {method['name']} (args: {', '.join(f'{arg['name']}:{arg['type'] or 'Any'}' for arg in method['args'])}, "
                        f"returns: {method['return_type'] or 'None'}, "
                        f"docstring: {method['docstring'] or 'None'})"
                    )
                    lines.append(method_str)
                    if method['calls']:
                        lines.append(f"      Calls: {', '.join(method['calls'])}")
        return "\n".join(lines)