import ast
import os
from typing import Dict, Optional, Set

class CodebaseAnalyzer:
    def __init__(self):
        self.classes = {}  # file:class_name -> class_info
        self.imports = {}  # file -> set of imported names
        self.file_trees = {}  # file -> AST

    def analyze_file(self, file_path: str) -> Optional[ast.AST]:
        """Analyze a single Python file, track imports, and return the AST."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                source = file.read()
                tree = ast.parse(source)
                self.file_trees[file_path] = tree
                self._extract_classes(tree, file_path)
                self._extract_imports(tree, file_path)
                return tree
        except Exception as e:
            print(f"Error analyzing {file_path}: {str(e)}")
            return None

    def _extract_classes(self, tree: ast.AST, file_path: str) -> None:
        """Extract class information from the AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = self._extract_class_info(node, file_path)
                self.classes[f"{file_path}:{class_info['name']}"] = class_info

    def _extract_class_info(self, node: ast.ClassDef, file_path: str) -> Dict:
        """Extract information from a class definition."""
        class_info = {
            'name': node.name,
            'file': file_path,
            'line': node.lineno,
            'methods': [],
            'bases': [base.id if isinstance(base, ast.Name) else str(base) 
                     for base in node.bases]
        }

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._extract_method_info(item)
                class_info['methods'].append(method_info)

        return class_info

    def _extract_method_info(self, node: ast.FunctionDef) -> Dict:
        """Extract information from a method definition."""
        args = []
        for arg in node.args.args:
            arg_info = {
                'name': arg.arg,
                'type': (ast.unparse(arg.annotation) 
                        if arg.annotation else None)
            }
            args.append(arg_info)

        return_type = (ast.unparse(node.returns) 
                      if node.returns else None)

        return {
            'name': node.name,
            'line': node.lineno,
            'args': args,
            'return_type': return_type,
            'docstring': ast.get_docstring(node)
        }

    def _extract_imports(self, tree: ast.AST, file_path: str) -> None:
        """Extract import statements to track dependencies."""
        imported_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imported_names.add(name.name.split('.')[0])  # Top-level module/class
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported_names.add(node.module.split('.')[0])
                for name in node.names:
                    imported_names.add(name.name)
        self.imports[file_path] = imported_names

    def analyze_directory(self, directory: str) -> Dict[str, ast.AST]:
        """Analyze all Python files in a directory and return file -> AST mapping."""
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    self.analyze_file(full_path)
        return self.file_trees

    def resolve_dependencies(self) -> Dict[str, Set[str]]:
        """Resolve class dependencies across files based on imports and bases."""
        dependencies = {}
        for file_path, class_info_dict in self.classes.items():
            class_name = class_info_dict['name']
            bases = class_info_dict['bases']
            deps = set()
            
            # Check imports in this file
            file_imports = self.imports.get(file_path, set())
            
            # Match bases with imported names or classes in other files
            for base in bases:
                # Check if base is imported from another file
                if base in file_imports:
                    deps.add(base)
                # Check if base is a class defined in another file
                for other_file, other_info in self.classes.items():
                    if other_file != file_path and other_info['name'] == base:
                        deps.add(f"{other_file}:{base}")
            
            dependencies[f"{file_path}:{class_name}"] = deps
        return dependencies

    def print_analysis(self) -> None:
        """Print the analyzed class and method information."""
        for class_key, class_info in self.classes.items():
            print(f"\nClass: {class_info['name']}")
            print(f"File: {class_info['file']} (line {class_info['line']})")
            if class_info['bases']:
                print(f"Inherits from: {', '.join(class_info['bases'])}")
            
            if class_info['methods']:
                print("Methods:")
                for method in class_info['methods']:
                    print(f"  {method['name']} (line {method['line']})")
                    if method['args']:
                        args_str = ', '.join(
                            f"{arg['name']}: {arg['type'] or 'Any'}" 
                            for arg in method['args']
                        )
                        print(f"    Args: {args_str}")
                    if method['return_type']:
                        print(f"    Returns: {method['return_type']}")
                    if method['docstring']:
                        print(f"    Docstring: {method['docstring']}")
        """Print the analyzed class and method information."""
        for class_key, class_info in self.classes.items():
            print(f"\nClass: {class_info['name']}")
            print(f"File: {class_info['file']} (line {class_info['line']})")
            if class_info['bases']:
                print(f"Inherits from: {', '.join(class_info['bases'])}")
            
            if class_info['methods']:
                print("Methods:")
                for method in class_info['methods']:
                    print(f"  {method['name']} (line {method['line']})")
                    if method['args']:
                        args_str = ', '.join(
                            f"{arg['name']}: {arg['type'] or 'Any'}" 
                            for arg in method['args']
                        )
                        print(f"    Args: {args_str}")
                    if method['return_type']:
                        print(f"    Returns: {method['return_type']}")
                    if method['docstring']:
                        print(f"    Docstring: {method['docstring']}")