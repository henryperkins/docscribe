# config/config_loader.py

import os
import json
import logging

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

def load_config(config_path='config.json'):
    """
    Loads and validates configuration settings based on the environment.

    Parameters:
        config_path (str): The base path to the configuration file.

    Returns:
        dict: The validated configuration settings.
    """
    try:
        env = os.getenv('ENV', 'development')
        env_config_path = f"config/config.{env}.json"
        if not os.path.exists(env_config_path):
            logger.error(f"Environment-specific config file '{env_config_path}' not found.")
            return {}
        with open(env_config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        # Override API key from environment if available
        config['openai_api_key'] = os.getenv('OPENAI_API_KEY', config.get('openai_api_key'))
        if not validate_config(config):
            logger.error("Configuration validation failed.")
            return {}
        logger.debug(f"Configuration loaded and validated from '{env_config_path}'.")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration from '{env_config_path}': {e}")
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
