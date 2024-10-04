# config/config_loader.py

import os
import json
import logging

logger = logging.getLogger(__name__)

def load_config(config_path='config.json'):
    """
    Loads configuration settings from a JSON file.

    Parameters:
        config_path (str): The path to the configuration file.

    Returns:
        dict: The configuration settings.
    """
    try:
        if not os.path.exists(config_path):
            logger.error(f"Configuration file '{config_path}' not found.")
            return {}
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.debug(f"Configuration loaded from '{config_path}'.")
        return config
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
