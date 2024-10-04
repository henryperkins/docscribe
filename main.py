# main.py

import asyncio
import logging
import json
from pathlib import Path
from typing import Optional

from config import load_config, load_function_schema
from io import (
    get_all_file_paths,
    read_file_async,
    write_file_async,
    backup_file,
    validate_file
)
from parser import (
    extract_python_structure,
    extract_javascript_structure,
    extract_html_structure,
    extract_css_structure
)
from docs import generate_documentation_report
from api.openai_client import call_api, fetch_documentation, summarize_text
from utils import (
    get_language_from_extension,
    format_code,
    clean_code,
    generate_documentation_prompt,
    chunk_text,
    is_binary_file
)

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed logs, change to INFO or WARNING in production
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DocScribe")

async def process_file(
    file_path: str,
    config: dict,
    function_schema: dict
) -> Optional[dict]:
    """
    Processes a single file: extracts structure, generates documentation, inserts documentation into code, and returns documentation data.
    
    Parameters:
        file_path (str): Path to the file.
        config (dict): Configuration settings.
        function_schema (dict): Function schema for API interactions.
    
    Returns:
        Optional[dict]: Documentation data or None if processing fails.
    """
    skip_types = set(config.get("skip_extensions", []))
    if not validate_file(file_path, skip_types):
        logger.debug(f"Skipping file '{file_path}' due to validation.")
        return None
    
    language = get_language_from_extension(file_path)
    if language == "unsupported":
        logger.warning(f"Unsupported language for file '{file_path}'. Skipping.")
        return None
    
    content = await read_file_async(file_path)
    if not content:
        logger.warning(f"No content found in file '{file_path}'. Skipping.")
        return None
    
    # Clean and format code
    cleaned_code = clean_code(content)
    formatted_code = format_code(cleaned_code)
    
    # Extract code structure based on language
    if language == "python":
        code_structure = extract_python_structure(formatted_code, config.get("context_keywords", {}))
    elif language == "javascript":
        code_structure = extract_javascript_structure(file_path, formatted_code, language, function_schema)
    elif language == "html":
        code_structure = extract_html_structure(formatted_code)
    elif language == "css":
        code_structure = extract_css_structure(formatted_code)
    else:
        logger.warning(f"Language '{language}' not supported for file '{file_path}'.")
        return None
    
    if not code_structure:
        logger.warning(f"No structure extracted from '{file_path}'. Skipping.")
        return None
    
    # Generate documentation prompt
    prompt = generate_documentation_prompt(
        file_name=Path(file_path).name,
        code_structure=code_structure,
        project_info=config.get("project_info"),
        style_guidelines=config.get("style_guidelines"),
        language=language
    )
    
    # Fetch documentation from OpenAI API
    async with aiohttp.ClientSession() as session:
        documentation = await fetch_documentation(
            session=session,
            prompt=prompt,
            semaphore=asyncio.Semaphore(config.get("concurrency", 5)),
            model_name=config.get("openai_model", "gpt-4"),
            function_schema=function_schema
        )
    
    if not documentation:
        logger.error(f"Failed to generate documentation for '{file_path}'.")
        return None
    
    # Optionally summarize high-relevance elements
    for element in documentation.get("elements", []):
        if element.get("context_relevance_score") == "High":
            summary = await summarize_text(
                session=session,
                text=element.get("description", ""),
                semaphore=asyncio.Semaphore(config.get("concurrency", 5))
            )
            if summary:
                element["summary"] = summary
    
    # Chunk documentation if necessary
    for element in documentation.get("elements", []):
        if len(element.get("description", "")) > config.get("chunk_max_length", 500):
            element["description_chunks"] = chunk_text(element["description"], config.get("chunk_max_length", 500))
        else:
            element["description_chunks"] = [element["description"]]
    
    # Insert documentation into code
    if language == "python":
        from parser.python_parser import insert_docstrings as insert_python_docstrings
        modified_code = insert_python_docstrings(formatted_code, documentation)
    elif language == "javascript":
        from parser.javascript_parser import insert_docstrings as insert_javascript_docstrings
        modified_code = insert_javascript_docstrings(formatted_code, documentation, language)
    elif language == "html":
        from parser.html_parser import insert_comments as insert_html_comments
        modified_code = insert_html_comments(formatted_code, documentation)
    elif language == "css":
        from parser.css_parser import insert_comments as insert_css_comments
        modified_code = insert_css_comments(formatted_code, documentation)
    else:
        modified_code = formatted_code  # No insertion for unsupported languages
    
    # Backup original file
    backup_file(file_path)
    
    # Write modified code back to file
    await write_file_async(file_path, modified_code)
    
    # Prepare data for documentation report
    return documentation

async def main():
    """
    Main entry point for DocScribe.
    """
    # Load configuration
    config = load_config("config/config.json")
    function_schema = load_function_schema("config/function_schema.json")
    
    root_dir = config.get("root_dir", ".")
    excluded_dirs = set(config.get("exclude_dirs", []))
    excluded_files = set(config.get("exclude_files", []))
    skip_extensions = set(config.get("skip_extensions", []))
    
    # Retrieve all relevant file paths
    file_paths = get_all_file_paths(
        repo_path=root_dir,
        excluded_dirs=excluded_dirs,
        excluded_files=excluded_files,
        skip_types=skip_extensions
    )
    
    if not file_paths:
        logger.warning("No files found to process.")
        return
    
    documentation_data = []
    
    # Process files concurrently with limited concurrency
    semaphore = asyncio.Semaphore(config.get("concurrency", 5))
    tasks = [
        asyncio.create_task(process_file(fp, config, function_schema))
        for fp in file_paths
    ]
    
    for task in asyncio.as_completed(tasks):
        doc = await task
        if doc:
            documentation_data.append(doc)
    
    if not documentation_data:
        logger.warning("No documentation data generated.")
        return
    
    # Generate documentation report
    report = {}
    for doc in documentation_data:
        report.setdefault("elements", []).extend(doc.get("elements", []))
    
    generate_documentation_report(report, output_file=config.get("output_file", "documentation.md"))
    logger.info(f"Documentation report generated at '{config.get('output_file', 'documentation.md')}'.")
    
if __name__ == "__main__":
    asyncio.run(main())
