# parser/python_parser.py

import ast
import logging
import astor  # Install astor via 'pip install astor'

logger = logging.getLogger(__name__)

def extract_structure(code):
    """
    Parses Python code to extract functions and classes.

    Parameters:
        code (str): The Python code.

    Returns:
        dict: Structure containing functions and classes.
    """
    try:
        tree = ast.parse(code)
        structure = {'functions': [], 'classes': []}

        # Helper function to set parent nodes
        def set_parents(node, parent=None):
            for child in ast.iter_child_nodes(node):
                child.parent = node
                set_parents(child, node)

        set_parents(tree)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not isinstance(getattr(node, 'parent', None), ast.ClassDef):
                    func = {
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'docstring': ast.get_docstring(node),
                        'async': isinstance(node, ast.AsyncFunctionDef)
                    }
                    structure['functions'].append(func)
            elif isinstance(node, ast.ClassDef):
                cls = {
                    'name': node.name,
                    'docstring': ast.get_docstring(node),
                    'methods': []
                }
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method = {
                            'name': child.name,
                            'args': [arg.arg for arg in child.args.args],
                            'docstring': ast.get_docstring(child),
                            'async': isinstance(child, ast.AsyncFunctionDef)
                        }
                        cls['methods'].append(method)
                structure['classes'].append(cls)
        return structure
    except Exception as e:
        logger.error(f"Error extracting structure: {e}")
        return None

def insert_docstrings(code, documentation):
    """
    Inserts docstrings into Python code.

    Parameters:
        code (str): Original code.
        documentation (dict): Documentation to insert.

    Returns:
        str: Code with inserted docstrings.
    """
    try:
        tree = ast.parse(code)
        docstrings_mapping = {}

        if 'functions' in documentation:
            for func_doc in documentation['functions']:
                name = func_doc.get('name')
                doc = func_doc.get('docstring', '')
                if name and doc:
                    docstrings_mapping[name] = doc

        if 'classes' in documentation:
            for class_doc in documentation['classes']:
                class_name = class_doc.get('name')
                class_docstring = class_doc.get('docstring', '')
                if class_name and class_docstring:
                    docstrings_mapping[class_name] = class_docstring
                methods = class_doc.get('methods', [])
                for method_doc in methods:
                    method_name = method_doc.get('name')
                    full_method_name = f"{class_name}.{method_name}"
                    method_docstring = method_doc.get('docstring', '')
                    if method_name and method_docstring:
                        docstrings_mapping[full_method_name] = method_docstring

        # Insert docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                parent = getattr(node, 'parent', None)
                if isinstance(parent, ast.ClassDef):
                    full_name = f"{parent.name}.{node.name}"
                else:
                    full_name = node.name
                if full_name in docstrings_mapping:
                    doc_content = docstrings_mapping[full_name]
                    docstring_node = ast.Expr(value=ast.Constant(value=doc_content))
                    if ast.get_docstring(node):
                        node.body[0] = docstring_node  # Replace existing docstring
                    else:
                        node.body.insert(0, docstring_node)
            elif isinstance(node, ast.ClassDef):
                if node.name in docstrings_mapping:
                    doc_content = docstrings_mapping[node.name]
                    docstring_node = ast.Expr(value=ast.Constant(value=doc_content))
                    if ast.get_docstring(node):
                        node.body[0] = docstring_node  # Replace existing docstring
                    else:
                        node.body.insert(0, docstring_node)
        # Unparse the AST back to code
        modified_code = astor.to_source(tree)
        return modified_code
    except Exception as e:
        logger.error(f"Error inserting docstrings: {e}")
        return code
