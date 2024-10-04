# utils/helpers.py

import nltk
import logging
from typing import List

logger = logging.getLogger(__name__)

# Download NLTK data if not already present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def chunk_text(text: str, max_length: int = 500) -> List[str]:
    """
    Splits the text into chunks not exceeding max_length characters.
    
    Parameters:
        text (str): The text to split.
        max_length (int): Maximum number of characters per chunk.
    
    Returns:
        List[str]: A list of text chunks.
    """
    logger.debug("Starting text chunking.")
    sentences = nltk.sent_tokenize(text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_length:
            current_chunk += " " + sentence if current_chunk else sentence
        else:
            chunks.append(current_chunk)
            current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk)
    
    logger.debug(f"Created {len(chunks)} text chunks.")
    return chunks

def is_binary_file(file_path: str) -> bool:
    """
    Checks if a file is binary.
    
    Parameters:
        file_path (str): Path to the file.
    
    Returns:
        bool: True if binary, False otherwise.
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if b'\0' in chunk:
                logger.debug(f"File '{file_path}' is binary.")
                return True
        return False
    except Exception as e:
        logger.error(f"Error checking if file is binary '{file_path}': {e}", exc_info=True)
        return False
