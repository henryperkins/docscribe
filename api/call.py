# api/openai_client.py

import openai
import logging
from typing import Optional
from config.config_loader import load_config

logger = logging.getLogger(__name__)

# Load OpenAI API Key from configuration
CONFIG = load_config()
OPENAI_API_KEY = CONFIG.get("openai_api_key")

openai.api_key = OPENAI_API_KEY

def call_openai_api(
    prompt: str,
    model: str = "gpt-4",
    max_tokens: int = 150,
    temperature: float = 0.5
) -> Optional[str]:
    """
    Calls the OpenAI API with the given prompt and returns the response.
    
    Parameters:
        prompt (str): The prompt to send to the API.
        model (str): The OpenAI model to use.
        max_tokens (int): The maximum number of tokens to generate.
        temperature (float): Sampling temperature.
    
    Returns:
        Optional[str]: The generated text or None if the call fails.
    """
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key not set.")
        return None
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        generated_text = response.choices[0].message['content'].strip()
        logger.debug("OpenAI API call successful.")
        return generated_text
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API Error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error calling OpenAI API: {e}", exc_info=True)
        return None

def summarize_text(
    text: str,
    model: str = "gpt-4",
    max_tokens: int = 100,
    temperature: float = 0.3
) -> Optional[str]:
    """
    Summarizes the given text using OpenAI's GPT-4 model.
    
    Parameters:
        text (str): The text to summarize.
        model (str): The OpenAI model to use.
        max_tokens (int): The maximum number of tokens in the summary.
        temperature (float): Sampling temperature.
    
    Returns:
        Optional[str]: The summarized text or None if summarization fails.
    """
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key not set.")
        return None
    try:
        prompt = (
            "Please provide a concise summary of the following text with a focus on its relevance to AI context window management:\n\n"
            f"{text}"
        )
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a concise summarizer specialized in technical documentation."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        summary = response.choices[0].message['content'].strip()
        logger.debug("Text summarization successful.")
        return summary
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API Error during summarization: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during text summarization: {e}", exc_info=True)
        return None
