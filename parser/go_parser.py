# parser/go_parser.py

import re
import logging

logger = logging.getLogger(__name__)

def extract_structure(code):
    """
    Parses Go code to extract functions and methods.

    Parameters:
        code (str): The Go code as a string.

    Returns:
        dict: Structure containing functions and methods.
    """
    try:
        structure = {'functions': [], 'methods': []}

        # Regular expression patterns
        function_pattern = re.compile(r'func\s+(\w+)\s*\((.*?)\)\s*(\((.*?)\))?')
        method_pattern = re.compile(r'func\s+\((\w+\s+\*?\w+)\)\s+(\w+)\s*\((.*?)\)\s*(\((.*?)\))?')

        lines = code.split('\n')
        for line in lines:
            line = line.strip()
            # Check for method definitions
            method_match = method_pattern.match(line)
            if method_match:
                receiver = method_match.group(1)
                method_name = method_match.group(2)
                params = method_match.group(3)
                return_values = method_match.group(5)
                method_info = {
                    'name': method_name,
                    'receiver': receiver,
                    'parameters': params.split(',') if params else [],
                    'return_values': return_values.split(',') if return_values else [],
                    'docstring': ''  # No comment extraction in this simplified example
                }
                structure['methods'].append(method_info)
                continue

            # Check for function definitions
            function_match = function_pattern.match(line)
            if function_match:
                function_name = function_match.group(1)
                params = function_match.group(2)
                return_values = function_match.group(4)
                function_info = {
                    'name': function_name,
                    'parameters': params.split(',') if params else [],
                    'return_values': return_values.split(',') if return_values else [],
                    'docstring': ''  # No comment extraction in this simplified example
                }
                structure['functions'].append(function_info)

        return structure
    except Exception as e:
        logger.error(f"Error parsing Go code: {e}")
        return None

def insert_docstrings(code, documentation):
    """
    Inserts docstrings into Go code by adding comments above functions and methods.

    Parameters:
        code (str): Original Go code.
        documentation (dict): Documentation to insert.

    Returns:
        str: Code with inserted docstrings.
    """
    try:
        lines = code.split('\n')
        code_with_docs = []
        index = 0

        while index < len(lines):
            line = lines[index]
            stripped_line = line.strip()
            inserted = False

            # Check for method definitions
            if stripped_line.startswith('func'):
                method_match = re.match(r'func\s+\((\w+\s+\*?\w+)\)\s+(\w+)\s*\(', stripped_line)
                if method_match:
                    method_name = method_match.group(2)
                    method_doc = next((m for m in documentation.get('methods', []) if m['name'] == method_name), None)
                    if method_doc and method_doc.get('docstring'):
                        docstring_lines = format_comment_go(method_doc['docstring'])
                        code_with_docs.extend(docstring_lines)
                        inserted = True
                else:
                    # Function definition
                    function_match = re.match(r'func\s+(\w+)\s*\(', stripped_line)
                    if function_match:
                        function_name = function_match.group(1)
                        function_doc = next((f for f in documentation.get('functions', []) if f['name'] == function_name), None)
                        if function_doc and function_doc.get('docstring'):
                            docstring_lines = format_comment_go(function_doc['docstring'])
                            code_with_docs.extend(docstring_lines)
                            inserted = True

            code_with_docs.append(line)
            index += 1

        modified_code = '\n'.join(code_with_docs)
        return modified_code

    except Exception as e:
        logger.error(f"Error inserting Go docstrings: {e}")
        return code

def format_comment_go(docstring):
    """
    Formats a docstring as a Go comment block.

    Parameters:
        docstring (str): The docstring to format.

    Returns:
        List[str]: Lines of the formatted docstring.
    """
    lines = docstring.strip().split('\n')
    formatted = [f'// {line}' for line in lines]
    return formatted
