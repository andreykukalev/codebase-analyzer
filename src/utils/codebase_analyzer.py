import os
import ast
from typing import Dict, List
from pathlib import Path

class CodebaseAnalyzer:
    def __init__(self):
        self.classes = {}
        self.file_trees = {}

    def analyze_file(self, file_path: str) -> ast.AST:
        """Analyzes single source code file utilizing AST parser."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                source = file.read()
                tree = ast.parse(source)
                self.file_trees[file_path] = tree
                self._extract_classes(tree, file_path)
                return tree
        except Exception as e:
            print(f"Error analyzing {file_path}: {str(e)}")
            return None

    def _extract_classes(self, tree: ast.AST, file_path: str) -> None:
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = self._extract_class_info(node, file_path)
                self.classes[f"{file_path}:{class_info['name']}"] = class_info

    def _extract_class_info(self, node: ast.ClassDef, file_path: str) -> Dict:
        class_info = {
            'name': node.name,
            'file': file_path,
            'line': node.lineno,
            'methods': [],
            'bases': [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases]
        }
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._extract_method_info(item)
                class_info['methods'].append(method_info)
        return class_info

    def _extract_method_info(self, node: ast.FunctionDef) -> Dict:
        """Extract method info, safely handling args and returns."""
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
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)
        return calls

    def analyze_directory(self, directory: str) -> Dict[str, ast.AST]:
        """Scans codebase directory and processes python files."""

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    self.analyze_file(os.path.join(root, file))
        return self.file_trees

    def write_trees_to_files(self, output_dir: Path) -> None:
        """Writes all extracted AST trees and collected class data to separate files."""

        if not self.file_trees:
            print("No data available to write.")
            return

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Group classes by file
        classes_by_file = {}
        for key, class_info in self.classes.items():
            file_path = class_info['file']
            if file_path not in classes_by_file:
                classes_by_file[file_path] = []
            classes_by_file[file_path].append(class_info)

        # Write data for each file
        for file_path in self.file_trees:
            base_name = os.path.basename(file_path).replace('.py', '')

            # Write AST
            ast_output_file = os.path.join(output_dir, f"{base_name}_ast.txt")
            ast_text = ast.dump(self.file_trees[file_path], indent=2)
            with open(ast_output_file, 'w', encoding='utf-8') as f:
                f.write(ast_text)
            print(f"AST for {file_path} written to {ast_output_file}")

            # Write class data
            class_output_file = os.path.join(output_dir, f"{base_name}_classes.txt")
            with open(class_output_file, 'w', encoding='utf-8') as f:
                if file_path in classes_by_file:
                    for class_info in classes_by_file[file_path]:
                        f.write(f"Class: {class_info['name']}\n")
                        f.write(f"Line: {class_info['line']}\n")
                        if class_info['bases']:
                            f.write(f"Inherits from: {', '.join(class_info['bases'])}\n")
                        if class_info['methods']:
                            f.write("Methods:\n")
                            for method in class_info['methods']:
                                f.write(f"  {method['name']} (line {method['line']})\n")
                                if method['args']:
                                    args_str = ', '.join(
                                        f"{arg['name']}: {arg['type'] or 'Any'}" 
                                        for arg in method['args']
                                    )
                                    f.write(f"    Args: {args_str}\n")
                                if method['return_type']:
                                    f.write(f"    Returns: {method['return_type']}\n")
                                if method['docstring']:
                                    f.write(f"    Docstring: {method['docstring']}\n")
                        f.write("\n")
                else:
                    f.write("No classes found in this file.\n")
            print(f"Class data for {file_path} written to {class_output_file}")

    @staticmethod
    def serialize_classes_to_string(classes: Dict) -> str:
        """Serializes the dictionary with classes info structure to a string."""

        if not classes:
            return "Classes: None"

        lines = ["Classes:"]
        for class_key, class_info in classes.items():
            class_str = (f"- {class_key} (name: {class_info['name']}, file: {class_info['file']}, "
                        f"line: {class_info['line']})")
            lines.append(class_str)
            if class_info['bases']:
                lines.append(f"  Inherits: {', '.join(class_info['bases'])}")
            if class_info['methods']:
                lines.append("  Methods:")
                for method in class_info['methods']:
                    method_str = (f"    - {method['name']} (args: {', '.join(f"{arg['name']}:{arg['type'] or 'Any'}" for arg in method['args'])}, "
                                 f"returns: {method['return_type'] or 'None'}, "
                                 f"docstring: {method['docstring'] or 'None'})")
                    lines.append(method_str)
                    if method['calls']:
                        lines.append(f"      Calls: {', '.join(method['calls'])}")
        return "\n".join(lines)