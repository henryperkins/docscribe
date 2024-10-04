# parser/html_parser.py

from bs4 import BeautifulSoup, Comment
import logging

logger = logging.getLogger(__name__)

def extract_structure(code):
    """
    Parses HTML code to extract tags and attributes.

    Parameters:
        code (str): The HTML code.

    Returns:
        dict: Structure containing tags and attributes.
    """
    try:
        soup = BeautifulSoup(code, 'html.parser')
        tags = []
        for tag in soup.find_all(True):
            tags.append({'name': tag.name, 'attrs': tag.attrs})
        return {'tags': tags}
    except Exception as e:
        logger.error(f"Error extracting HTML structure: {e}")
        return None

def insert_comments(code, documentation):
    """
    Inserts comments into HTML code.

    Parameters:
        code (str): Original code.
        documentation (dict): Documentation to insert.

    Returns:
        str: Code with inserted comments.
    """
    try:
        soup = BeautifulSoup(code, 'html.parser')
        # Insert documentation as a comment at the beginning
        comments = []
        if 'summary' in documentation:
            comments.append(f"Summary: {documentation['summary']}")
        if 'changes_made' in documentation:
            changes = '; '.join(documentation['changes_made'])
            comments.append(f"Changes: {changes}")

        comment_text = ' | '.join(comments)
        comment = Comment(f" {comment_text} ")
        if soup.contents:
            soup.insert(0, '\n')
            soup.insert(0, comment)
        else:
            soup.append(comment)
        modified_code = str(soup)
        return modified_code
    except Exception as e:
        logger.error(f"Error inserting HTML comments: {e}")
        return code
