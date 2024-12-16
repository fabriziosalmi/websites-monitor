import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def check_cdn(website: str) -> str:
    """
    Checks if a website is using a CDN by inspecting the server header.

    Args:
        website (str): The URL of the website to check.

    Returns:
        str:
            - "🟢" if a CDN is detected.
            - "⚪" if no CDN is detected or an error occurs.
    """
    try:
        response = requests.get(website, stream=True, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        if 'server' in response.headers:
            server_header = response.headers['server'].lower()
            if 'cloudflare' in server_header or 'akamai' in server_header or 'fastly' in server_header or 'amazon' in server_header or 'cdn' in server_header or "stackpath" in server_header:
                logger.info(f"CDN detected for {website}.")
                return "🟢"
        logger.info(f"No CDN detected for {website}.")
        return "⚪"
    except requests.exceptions.RequestException as e:
        logger.error(f"Error during CDN check for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"An unexpected error occurred during the CDN check for {website}: {e}")
        return "⚪"
