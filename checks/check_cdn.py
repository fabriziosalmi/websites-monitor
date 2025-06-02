import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def check_cdn(website: str) -> str:
    """
    Checks if a website is using a CDN by inspecting headers and other indicators.

    Args:
        website (str): The URL of the website to check.

    Returns:
        str:
            - "🟢" if a CDN is detected.
            - "🔴" if no CDN is detected.
            - "⚪" if an error occurs.
    """
    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        'User-Agent': 'CDNChecker/1.0'
    }

    try:
        response = requests.get(website, headers=headers, stream=True, timeout=10)
        response.raise_for_status()

        # Check server header for CDN indicators
        server_header = response.headers.get('server', '').lower()
        cdn_indicators = ['cloudflare', 'akamai', 'fastly', 'amazon', 'cdn', 'stackpath', 'keycdn', 'maxcdn']
        
        if any(indicator in server_header for indicator in cdn_indicators):
            logger.info(f"CDN detected in server header for {website}.")
            return "🟢"

        # Check other headers that might indicate CDN usage
        cdn_headers = [
            'cf-ray',  # Cloudflare
            'x-served-by',  # Fastly
            'x-cache',  # Various CDNs
            'x-edge-location',  # AWS CloudFront
            'x-akamai-transformed'  # Akamai
        ]
        
        if any(header in response.headers for header in cdn_headers):
            logger.info(f"CDN detected in headers for {website}.")
            return "🟢"

        logger.info(f"No CDN detected for {website}.")
        return "🔴"

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error during CDN check for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"An unexpected error occurred during the CDN check for {website}: {e}")
        return "⚪"
