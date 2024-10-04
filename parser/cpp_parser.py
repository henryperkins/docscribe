# parser/cpp_parser.py

import clang.cindex
import logging
import os

logger = logging.getLogger(__name__)

# Set the library path for libclang
# You may need to adjust this path based on your system
clang.cindex.Config.set_library_file('/usr/lib/llvm-10/lib/libclang-10.so.1')

def extract_structure(code, file_name='temp.cpp'):
    """
    Parses C++ code to extract classes, functions, and methods.

    Parameters:
        code (str): The C++ code as a string.
        file_name (str): A temporary file name to use for parsing.

    Returns:
        dict: Structure containing classes and functions.
    """
    try:
        # Write code to a temporary file
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(code)
        
        index = clang.cindex.Index.create()
        tu = index.parse(file_name, args=['-std=c++11'])

        structure = {'functions': [], 'classes': []}

        for cursor in tu.cursor.get_children():
            if cursor.kind == clang.cindex.CursorKind.FUNCTION_DECL:
                func = {
                    'name': cursor.spelling,
                    'args': [arg.spelling for arg in cursor.get_arguments()],
                    'result_type': cursor.result_type.spelling,
                    'docstring': extract_comment(cursor)
                }
                structure['functions'].append(func)
            elif cursor.kind == clang.cindex.CursorKind.CLASS_DECL:
                cls = {
                    'name': cursor.spelling,
                    'docstring': extract_comment(cursor),
                    'methods': []
                }
                for c in cursor.get_children():
                    if c.kind == clang.cindex.CursorKind.CXX_METHOD:
                        method = {
                            'name': c.spelling,
                            'args': [arg.spelling for arg in c.get_arguments()],
                            'result_type': c.result_type.spelling,
                            'docstring': extract_comment(c),
                            'access_specifier': c.access_specifier.name
                        }
                        cls['methods'].append(method)
                structure['classes'].append(cls)

        # Clean up temporary file
        os.remove(file_name)
        return structure
    except Exception as e:
        logger.error(f"Error parsing C++ code: {e}")
        return None

def extract_comment(cursor):
    """
    Extracts the documentation comment associated with a cursor.

    Parameters:
        cursor: A clang.cindex Cursor object.

    Returns:
        str: The extracted comment or an empty string.
    """
    raw_comment = cursor.raw_comment
    if raw_comment:
        return raw_comment.strip()
    return ''

def insert_docstrings(code, documentation):
    """
    Inserts docstrings into C++ code by adding comments above functions and classes.

    Parameters:
        code (str): Original C++ code.
        documentation (dict): Documentation to insert.

    Returns:
        str: Code with inserted docstrings.
    """
    try:
        # Similar to the Java example, we'll insert comments above definitions.

        lines = code.split('\n')
        code_with_docs = []
        index = 0

        while index < len(lines):
            line = lines[index]
            stripped_line = line.strip()
            inserted = False

            # Check for class definitions
            if stripped_line.startswith('class '):
                class_name = stripped_line.split(' ')[1].split('{')[0]
                class_doc = next((cls for cls in documentation.get('classes', []) if cls['name'] == class_name), None)
                if class_doc and class_doc.get('docstring'):
                    docstring_lines = format_comment_cpp(class_doc['docstring'])
                    code_with_docs.extend(docstring_lines)
                    inserted = True

            # Check for function definitions
            if '(' in stripped_line and ')' in stripped_line and ('{' in stripped_line or ';' in stripped_line):
                func_name = extract_function_name_cpp(stripped_line)
                # First, check in functions
                func_doc = next((func for func in documentation.get('functions', []) if func['name'] == func_name), None)
                if func_doc and func_doc.get('docstring'):
                    docstring_lines = format_comment_cpp(func_doc['docstring'])
                    code_with_docs.extend(docstring_lines)
                    inserted = True
                else:
                    # Then, check in methods
                    parent_class = get_enclosing_class_cpp(lines, index)
                    if parent_class:
                        class_doc = next((cls for cls in documentation.get('classes', []) if cls['name'] == parent_class), None)
                        if class_doc:
                            method_doc = next((m for m in class_doc.get('methods', []) if m['name'] == func_name), None)
                            if method_doc and method_doc.get('docstring'):
                                docstring_lines = format_comment_cpp(method_doc['docstring'])
                                code_with_docs.extend(docstring_lines)
                                inserted = True

            code_with_docs.append(line)
            index += 1

        modified_code = '\n'.join(code_with_docs)
        return modified_code

    except Exception as e:
        logger.error(f"Error inserting C++ docstrings: {e}")
        return code

def format_comment_cpp(docstring):
    """
    Formats a docstring as a C++ comment block.

    Parameters:
        docstring (str): The docstring to format.

    Returns:
        List[str]: Lines of the formatted docstring.
    """
    lines = docstring.strip().split('\n')
    formatted = ['/**']
    for line in lines:
        formatted.append(f' * {line}')
    formatted.append(' */')
    return formatted

def extract_function_name_cpp(signature):
    """
    Extracts the function name from a function signature.

    Parameters:
        signature (str): The function signature.

    Returns:
        str: The function name.
    """
    # Remove possible return type
    signature = signature.lstrip()
    if ' ' in signature:
        signature = ' '.join(signature.split(' ')[1:])
    # Get name before the '('
    name = signature.split('(')[0].strip()
    # Remove any qualifiers
    name = name.split('::')[-1]
    return name

def get_enclosing_class_cpp(lines, index):
    """
    Determines the enclosing class name for a given line index in C++ code.

    Parameters:
        lines (List[str]): The lines of code.
        index (int): The current line index.

    Returns:
        str: The name of the enclosing class or None.
    """
    brace_count = 0
    while index >= 0:
        line = lines[index].strip()
        if '{' in line:
            brace_count -= line.count('{')
        if '}' in line:
            brace_count += line.count('}')
            if brace_count == 1:
                # Possible start of a class
                if line.startswith('class '):
                    class_name = line.split(' ')[1].split('{')[0]
                    return class_name
        index -= 1
    return None
