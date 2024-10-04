# api/openai_client.py

import os
import json
import aiohttp
import asyncio
import logging

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

async def call_api(session, payload):
    """
    Makes an API call to OpenAI.

    Parameters:
        session (aiohttp.ClientSession): The HTTP session.
        payload (dict): The payload for the API call.

    Returns:
        dict: The API response.
    """
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    try:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status != 200:
                text = await response.text()
                logger.error(f"OpenAI API error {response.status}: {text}")
                return None
            return await response.json()
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        return None

async def fetch_documentation(session, prompt, semaphore, model_name, function_schema, retry=3):
    """
    Retrieves documentation content from the OpenAI API.

    Parameters:
        session (aiohttp.ClientSession): The HTTP session.
        prompt (str): The prompt to send.
        semaphore (asyncio.Semaphore): Concurrency semaphore.
        model_name (str): The model to use.
        function_schema (dict): The function schema.
        retry (int): Number of retry attempts.

    Returns:
        dict: The documentation content.
    """
    for attempt in range(retry):
        async with semaphore:
            payload = {
                'model': model_name,
                'messages': [
                    {'role': 'system', 'content': 'You are an assistant that generates code documentation.'},
                    {'role': 'user', 'content': prompt}
                ],
                'functions': [function_schema],
                'function_call': 'auto'
            }
            response = await call_api(session, payload)
            if response:
                try:
                    choice = response['choices'][0]
                    message = choice['message']
                    if 'function_call' in message:
                        arguments = message['function_call']['arguments']
                        documentation = json.loads(arguments)
                        return documentation
                    else:
                        logger.error("No function_call in API response.")
                        return None
                except Exception as e:
                    logger.error(f"Error processing API response: {e}")
                    return None
            else:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    return None
