# utils/helpers.py

import os
import logging
import subprocess
import black
import re

logger = logging.getLogger(__name__)

LANGUAGE_MAPPING = {
    '.py': 'python',
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.html': 'html',
    '.htm': 'html',
    '.css': 'css',
    # Add other mappings as needed
}

def get_language_from_extension(file_path):
    """
    Detects programming language based on file extension.

    Parameters:
        file_path (str): The path to the file.

    Returns:
        str: The language or 'unsupported' if not recognized.
    """
    _, ext = os.path.splitext(file_path)
    return LANGUAGE_MAPPING.get(ext.lower(), 'unsupported')

def format_code(code):
    """
    Formats code using Black.

    Parameters:
        code (str): The code to format.

    Returns:
        str: Formatted code.
    """
    try:
        formatted_code = black.format_str(code, mode=black.Mode())
        return formatted_code
    except Exception as e:
        logger.error(f"Error formatting code: {e}")
        return code

def clean_code(code):
    """
    Cleans code by removing unused imports and fixing issues.

    Parameters:
        code (str): The code to clean.

    Returns:
        str: Cleaned code.
    """
    try:
        result = subprocess.run(
            ['autoflake', '--remove-all-unused-imports', '--remove-unused-variables', '--in-place', '-'],
            input=code,
            text=True,
            capture_output=True
        )
        if result.returncode == 0:
            return result.stdout
        else:
            logger.error(f"Autoflake error: {result.stderr}")
            return code
    except Exception as e:
        logger.error(f"Error cleaning code: {e}")
        return code

def generate_documentation_prompt(file_name, code_structure, project_info, style_guidelines, language):
    """
    Generates a prompt for OpenAI API based on code structure.

    Returns:
        str: The generated prompt.
    """
    prompt = f"You are an experienced software developer tasked with generating comprehensive documentation.\n"

    if project_info:
        prompt += f"\nProject Information:\n{project_info}\n"
    if style_guidelines:
        prompt += f"\nStyle Guidelines:\n{style_guidelines}\n"

    prompt += f"\nFile Name: {file_name}"
    prompt += f"\nLanguage: {language}"
    prompt += f"\nCode Structure:\n{code_structure}"

    # Add instructions
    prompt += "\n\nPlease generate documentation for the above code structure following the style guidelines."

    return prompt
