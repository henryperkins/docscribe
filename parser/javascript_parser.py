# parser/javascript_parser.py

import subprocess
import json
import logging
import os

logger = logging.getLogger(__name__)

def extract_structure(file_path, code, language, function_schema):
    """
    Parses JavaScript/TypeScript code to extract functions and classes.

    Parameters:
        file_path (str): Path to the file.
        code (str): The code content.
        language (str): 'javascript' or 'typescript'.
        function_schema (dict): Schema for validation.

    Returns:
        dict: Extracted code structure.
    """
    try:
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'scripts', 'acorn_parser.js'
        )
        data_to_send = {
            'code': code,
            'language': language,
            'functionSchema': function_schema,
        }
        process = subprocess.run(
            ['node', script_path],
            input=json.dumps(data_to_send),
            capture_output=True,
            text=True
        )
        if process.returncode == 0:
            structure = json.loads(process.stdout)
            return structure
        else:
            logger.error(f"acorn_parser.js error: {process.stderr}")
            return None
    except Exception as e:
        logger.error(f"Error extracting JS/TS structure: {e}")
        return None

def insert_docstrings(code, documentation, language):
    """
    Inserts docstrings into JavaScript/TypeScript code.

    Parameters:
        code (str): Original code.
        documentation (dict): Documentation to insert.
        language (str): 'javascript' or 'typescript'.

    Returns:
        str: Code with inserted docstrings.
    """
    try:
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'scripts', 'acorn_inserter.js'
        )
        data_to_send = {
            'code': code,
            'documentation': documentation,
            'language': language,
        }
        process = subprocess.run(
            ['node', script_path],
            input=json.dumps(data_to_send),
            capture_output=True,
            text=True
        )
        if process.returncode == 0:
            modified_code = process.stdout
            return modified_code
        else:
            logger.error(f"acorn_inserter.js error: {process.stderr}")
            return code
    except Exception as e:
        logger.error(f"Error inserting JS/TS docstrings: {e}")
        return code
