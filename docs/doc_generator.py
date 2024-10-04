# docs/doc_generator.py

import os
import logging

logger = logging.getLogger(__name__)

def generate_summary(documentation):
    """
    Generates a summary section from documentation.

    Parameters:
        documentation (dict): Documentation data.

    Returns:
        str: Summary section in markdown.
    """
    if 'summary' in documentation:
        summary = documentation['summary'].strip()
        if summary:
            return f"## Summary\n\n{summary}\n"
    return ""

def generate_changes(documentation):
    """
    Generates a changes made section from documentation.

    Parameters:
        documentation (dict): Documentation data.

    Returns:
        str: Changes made section in markdown.
    """
    if 'changes_made' in documentation and documentation['changes_made']:
        changes = '\n'.join(f"- {change.strip()}" for change in documentation['changes_made'])
        return f"## Changes Made\n\n{changes}\n"
    return ""

def generate_functions_table(functions):
    """
    Generates a markdown table for functions.

    Parameters:
        functions (list): List of function documentation.

    Returns:
        str: Functions section in markdown.
    """
    if not functions:
        return "## Functions\n\nNo functions are defined in this file.\n\n"

    table = "## Functions\n\n"
    table += "| Function | Arguments | Description | Async |\n"
    table += "|----------|-----------|-------------|-------|\n"
    for func in functions:
        name = func.get('name', 'N/A')
        args = ', '.join(func.get('args', []))
        doc = func.get('docstring', 'No description provided.').splitlines()[0]
        is_async = "Yes" if func.get('async', False) else "No"
        table += f"| `{name}` | `{args}` | {doc} | {is_async} |\n"
    return table + "\n"

def generate_classes_section(classes):
    """
    Generates a classes section with methods.

    Parameters:
        classes (list): List of class documentation.

    Returns:
        str: Classes section in markdown.
    """
    if not classes:
        return "## Classes\n\nNo classes are defined in this file.\n\n"

    content = "## Classes\n\n"
    for cls in classes:
        name = cls.get('name', 'N/A')
        doc = cls.get('docstring', '')
        content += f"### Class: `{name}`\n\n{doc}\n\n"
        methods = cls.get('methods', [])
        if methods:
            content += "| Method | Arguments | Description | Async |\n"
            content += "|--------|-----------|-------------|-------|\n"
            for method in methods:
                method_name = method.get('name', 'N/A')
                args = ', '.join(method.get('args', []))
                method_doc = method.get('docstring', 'No description provided.').splitlines()[0]
                is_async = "Yes" if method.get('async', False) else "No"
                content += f"| `{method_name}` | `{args}` | {method_doc} | {is_async} |\n"
            content += "\n"
    return content

def compile_documentation(documentation, language, file_path, repo_root, new_content):
    """
    Aggregates all documentation parts into a complete report.

    Parameters:
        documentation (dict): Documentation data.
        language (str): Programming language.
        file_path (str): Path to the file.
        repo_root (str): Root directory of the repository.
        new_content (str): Content of the file with documentation inserted.

    Returns:
        str: Complete documentation report for the file.
    """
    try:
        relative_path = os.path.relpath(file_path, repo_root)
        file_header = f"# File: {relative_path}\n\n"
        summary_section = generate_summary(documentation)
        changes_section = generate_changes(documentation)
        functions_section = generate_functions_table(documentation.get('functions', []))
        classes_section = generate_classes_section(documentation.get('classes', []))
        code_block = f"```{language}\n{new_content}\n```\n\n---\n"
        documentation_content = (
            file_header +
            summary_section +
            changes_section +
            functions_section +
            classes_section +
            code_block
        )
        return documentation_content
    except Exception as e:
        logger.error(f"Error compiling documentation: {e}")
        return ""
