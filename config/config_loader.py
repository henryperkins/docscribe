# config/config_loader.py

import os
import json
import logging
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)

def validate_config(config):
    """
    Validates the loaded configuration.

    Parameters:
        config (dict): The configuration settings.

    Returns:
        bool: True if valid, False otherwise.
    """
    required_fields = [
        'root_dir',
        'exclude_dirs',
        'exclude_files',
        'skip_extensions',
        'context_keywords',
        'openai_api_key',
        'openai_model',
        'concurrency',
        'chunk_max_length',
        'output_file',
        'project_info',
        'style_guidelines'
    ]
    missing_fields = [field for field in required_fields if field not in config or not config[field]]
    if missing_fields:
        logger.error(f"Missing configuration fields: {', '.join(missing_fields)}")
        return False
    return True


class ConfigSchema(BaseModel):
    root_dir: str
    exclude_dirs: list
    exclude_files: list
    skip_extensions: list
    context_keywords: dict
    openai_api_key: str
    openai_model: str
    openai_max_tokens: int
    openai_temperature: float
    concurrency: int
    chunk_max_length: int
    output_file: str
    project_info: str
    style_guidelines: str

def load_config(config_path='config.json'):
    """
    Loads and validates configuration settings using pydantic.

    Parameters:
        config_path (str): The path to the configuration file.

    Returns:
        dict: The validated configuration settings.
    """
    try:
        if not os.path.exists(config_path):
            logger.error(f"Configuration file '{config_path}' not found.")
            return {}
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        # Override API key from environment if available
        config['openai_api_key'] = os.getenv('OPENAI_API_KEY', config.get('openai_api_key'))
        # Validate using pydantic
        validated_config = ConfigSchema(**config)
        logger.debug(f"Configuration loaded and validated from '{config_path}'.")
        return validated_config.dict()
    except ValidationError as ve:
        logger.error(f"Configuration validation error: {ve}")
        return {}
    except Exception as e:
        logger.error(f"Error loading configuration from '{config_path}': {e}")
        return {}

def load_function_schema(schema_path):
    """
    Loads a JSON schema for API interactions.

    Parameters:
        schema_path (str): The path to the JSON schema file.

    Returns:
        dict: The loaded JSON schema.
    """
    try:
        if not os.path.exists(schema_path):
            logger.error(f"Function schema file '{schema_path}' not found.")
            return {}
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        logger.debug(f"Function schema loaded from '{schema_path}'.")
        return schema
    except Exception as e:
        logger.error(f"Error loading function schema from '{schema_path}': {e}")
        return {}
