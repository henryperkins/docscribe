import os
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

async def write_documentation_report(
    documentation: Optional[Dict[str, Any]],
    language: str,
    file_path: str,
    repo_root: str,
    new_content: str,
) -> str:
    """Generates the documentation report content for a single file."""
    try:
        relative_path = os.path.relpath(file_path, repo_root)
        file_header = f"# File: {relative_path}\n\n"

        documentation_content = file_header
        documentation_content += _generate_summary_section(documentation)
        documentation_content += _generate_changes_section(documentation)
        documentation_content += generate_model_class_section(documentation.get('model_classes', []))
        documentation_content += _generate_functions_section(documentation.get('functions', []))
        documentation_content += _generate_classes_section(documentation.get('classes', []))
        documentation_content += _generate_code_block(new_content, language)

        return documentation_content
    except Exception as e:
        logger.error(
            f"Error generating documentation for '{file_path}': {e}", exc_info=True
        )
        return ""

def _generate_summary_section(documentation: Optional[Dict[str, Any]]) -> str:
    """Generates the summary section of the report."""
    try:
        summary = documentation.get("summary", "") if documentation else ""
        summary = _sanitize_text(summary)
        if summary:
            return f"## Summary\n\n{summary}\n"
        return ""
    except Exception as e:
        logger.error(f"Error in _generate_summary_section: {e}", exc_info=True)
        return ""


def generate_model_class_section(model_classes: List[Dict[str, Any]]) -> str:
    """Generates the model classes section of the report."""
    try:
        if not model_classes:
            return "## Model Classes\n\nNo model classes are defined in this file.\n\n"

        content = "## Model Classes\n\n"
        for model in model_classes:
            name = model.get('name', 'N/A')
            doc = _sanitize_text(model.get('docstring', ''))
            overview = _sanitize_text(model.get('overview', ''))
            content += f"### Model Class: `{name}`\n\n{doc}\n\n"
            content += f"#### Overview\n\n{overview}\n\n"
            attributes = model.get('attributes', [])
            if attributes:
                content += "| Attribute | Type | Description |\n"
                content += "|-----------|------|-------------|\n"
                for attr in attributes:
                    attr_name = attr.get('name', 'N/A')
                    attr_type = attr.get('type', 'N/A')
                    attr_doc = _sanitize_text(attr.get('docstring', ''))
                    first_line_attr_doc = attr_doc.splitlines()[0] if attr_doc else "No description provided."
                    content += f"| `{attr_name}` | `{attr_type}` | {first_line_attr_doc} |\n"
                content += "\n"
        return content
    except Exception as e:
        logger.error(f"Error in generate_model_class_section: {e}", exc_info=True)
        return ""


def _generate_changes_section(documentation: Optional[Dict[str, Any]]) -> str:
    """Generates the changes made section of the report."""
    try:
        changes = documentation.get("changes_made", []) if documentation else []
        changes = [_sanitize_text(change) for change in changes if change.strip()]
        if changes:
            changes_formatted = "\n".join(f"- {change}" for change in changes)
            return f"## Changes Made\n\n{changes_formatted}\n"
        return ""
    except Exception as e:
        logger.error(f"Error in _generate_changes_section: {e}", exc_info=True)
        return ""

def _generate_functions_section(functions: List[Dict[str, Any]]) -> str:
    """Generates the functions section of the report."""
    try:
        if not functions:
            return "## Functions\n\nNo functions are defined in this file.\n\n"

        table = "## Functions\n\n"
        table += "| Function | Arguments | Description | Async |\n"
        table += "|----------|-----------|-------------|-------|\n"
        for func in functions:
            name = func.get('name', 'N/A')
            args = ', '.join(func.get('args', []))
            doc = _sanitize_text(func.get('docstring', ''))
            first_line_doc = doc.splitlines()[0] if doc else "No description provided."
            is_async = "Yes" if func.get('async', False) else "No"
            table += f"| `{name}` | `{args}` | {first_line_doc} | {is_async} |\n"
        return table + "\n"
    except Exception as e:
        logger.error(f"Error in _generate_functions_section: {e}", exc_info=True)
        return ""

def _generate_classes_section(classes: List[Dict[str, Any]]) -> str:
    """Generates the classes section of the report."""
    try:
        if not classes:
            return "## Classes\n\nNo classes are defined in this file.\n\n"

        content = "## Classes\n\n"
        for cls in classes:
            name = cls.get('name', 'N/A')
            doc = _sanitize_text(cls.get('docstring', ''))
            content += f"### Class: `{name}`\n\n{doc}\n\n"
            methods = cls.get('methods', [])
            if methods:
                content += "| Method | Arguments | Description | Async | Type |\n"
                content += "|--------|-----------|-------------|-------|------|\n"
                for method in methods:
                    method_name = method.get('name', 'N/A')
                    args = ', '.join(method.get('args', []))
                    method_doc = _sanitize_text(method.get('docstring', ''))
                    first_line_method_doc = method_doc.splitlines()[0] if method_doc else "No description provided."
                    is_async = "Yes" if method.get('async', False) else "No"
                    method_type = method.get('type', 'N/A')
                    content += f"| `{method_name}` | `{args}` | {first_line_method_doc} | {is_async} | {method_type} |\n"
                content += "\n"
        return content
    except Exception as e:
        logger.error(f"Error in _generate_classes_section: {e}", exc_info=True)
        return ""

def _generate_code_block(new_content: str, language: str) -> str:
    """Generates the code block section of the report."""
    try:
        code_content = new_content.strip()
        return f"```{language}\n{code_content}\n```\n\n---\n"
    except Exception as e:
        logger.error(f"Error in _generate_code_block: {e}", exc_info=True)
        return ""

def _sanitize_text(text: str) -> str:
    """Removes excessive newlines and whitespace from the text."""
    try:
        if not text:
            return ""
        lines = text.strip().splitlines()
        sanitized_lines = [line.strip() for line in lines if line.strip()]
        return "\n".join(sanitized_lines)
    except Exception as e:
        logger.error(f"Error in _sanitize_text: {e}", exc_info=True)
        return ""

def generate_table_of_contents(markdown_content: str) -> str:
    """Generates a markdown table of contents from the given markdown content."""
    try:
        import re

        toc = []
        seen_anchors = set()
        for line in markdown_content.split("\n"):
            match = re.match("^(#{1,6})\\s+(.*)", line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                anchor = re.sub("[^\\w\\s\\-]", "", title).lower()
                anchor = re.sub("\\s+", "-", anchor)
                original_anchor = anchor
                counter = 1
                while anchor in seen_anchors:
                    anchor = f"{original_anchor}-{counter}"
                    counter += 1
                seen_anchors.add(anchor)
                indent = "  " * (level - 1)
                toc.append(f"{indent}- [{title}](#{anchor})")
        return "\n".join(toc)
    except Exception as e:
        logger.error(f"Error in generate_table_of_contents: {e}", exc_info=True)
        return ""
