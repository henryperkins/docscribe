```python
# io/file_manager.py

import os
import aiofiles
import logging
import shutil

logger = logging.getLogger(__name__)

async def read_file_async(file_path):
    """
    Asynchronously reads the content of a file.

    Parameters:
        file_path (str): The path to the file.

    Returns:
        str: The content of the file.
    """
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
        logger.debug(f"Read content from '{file_path}'.")
        return content
    except Exception as e:
        logger.error(f"Error reading file '{file_path}': {e}")
        return None


async def backup_file(file_path: str, new_content: str) -> None:
    """Creates a backup of the file and writes the new content."""
    backup_path = f"{file_path}.bak"
    try:
        if os.path.exists(backup_path):
            os.remove(backup_path)
            logger.debug(f"Removed existing backup at '{backup_path}'.")
        shutil.copy(file_path, backup_path)
        logger.debug(f"Backup created at '{backup_path}'.")

        # Write the new content to the original file
        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(new_content)
        logger.info(f"Inserted documentation into '{file_path}'.")

    except Exception as e:
        logger.error(f"Error writing to '{file_path}': {e}", exc_info=True)
        if os.path.exists(backup_path):
            shutil.copy(backup_path, file_path)
            os.remove(backup_path)
            logger.info(f"Restored original file from backup for '{file_path}'.")


def validate_file(file_path: str, skip_types: Set[str]) -> bool:
    """
    Validates a file by checking:
    1. If it exists and is a file.
    2. If its extension is not in the skip_types set.
    3. If it is not a binary file.

    Parameters:
        file_path (str): The path to the file.
        skip_types (Set[str]): Set of file extensions to skip.

    Returns:
        bool: True if the file is valid, False otherwise.
    """
    try:
        if not os.path.isfile(file_path):
            logger.debug(f"'{file_path}' is not a file.")
            return False

        _, ext = os.path.splitext(file_path)
        if ext.lower() in skip_types:
            logger.debug(f"Skipping '{file_path}' due to extension '{ext}'.")
            return False

        # Check if file is binary
        with open(file_path, 'rb') as f:
            if b'\0' in f.read(1024):
                logger.debug(f"Skipping binary file '{file_path}'.")
                return False

        return True

    except Exception as e:
        logger.error(f"Error validating file '{file_path}': {e}")
        return False
        

def get_all_file_paths(repo_path: str, excluded_dirs: Set[str], excluded_files: Set[str], skip_types: Set[str]) -> List[str]:
    """
    Retrieves all file paths based on exclusions and skips.

    Parameters:
        repo_path (str): The root directory to search for files.
        excluded_dirs (Set[str]): Directories to exclude.
        excluded_files (Set[str]): Files to exclude.
        skip_types (Set[str]): File extensions to skip.

    Returns:
        List[str]: A list of file paths.
    """
    file_paths = []
    for root, dirs, files in os.walk(repo_path, topdown=True):
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        for file in files:
            if file in excluded_files:
                continue
            file_path = os.path.join(root, file)
            if validate_file(file_path, skip_types):
                file_paths.append(file_path)
    logger.debug(f"Found {len(file_paths)} files in '{repo_path}'.")
    return file_paths
