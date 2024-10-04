# parser/css_parser.py

import tinycss2
import logging

logger = logging.getLogger(__name__)

def extract_structure(code):
    """
    Parses CSS code to extract selectors and declarations.

    Parameters:
        code (str): The CSS code.

    Returns:
        dict: Structure containing rules.
    """
    try:
        rules = tinycss2.parse_rule_list(code)
        css_rules = []
        for rule in rules:
            if rule.type == 'qualified-rule':
                selector = ''.join([t.serialize() for t in rule.prelude]).strip()
                declarations = []
                for token in tinycss2.parse_declaration_list(rule.content):
                    if token.type == 'declaration':
                        prop = token.lower_name
                        value = ''.join([t.serialize() for t in token.value]).strip()
                        declarations.append({'property': prop, 'value': value})
                css_rules.append({'selector': selector, 'declarations': declarations})
        return {'rules': css_rules}
    except Exception as e:
        logger.error(f"Error extracting CSS structure: {e}")
        return None

def insert_comments(code, documentation):
    """
    Inserts comments into CSS code.

    Parameters:
        code (str): Original code.
        documentation (dict): Documentation to insert.

    Returns:
        str: Code with inserted comments.
    """
    try:
        comments = []
        if 'summary' in documentation:
            comments.append(f"Summary: {documentation['summary']}")
        if 'changes_made' in documentation:
            changes = '; '.join(documentation['changes_made'])
            comments.append(f"Changes: {changes}")
        comment_text = ' | '.join(comments)
        comment = f"/* {comment_text} */\n"
        modified_code = comment + code
        return modified_code
    except Exception as e:
        logger.error(f"Error inserting CSS comments: {e}")
        return code
