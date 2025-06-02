import requests
import json
import logging
from requests.exceptions import RequestException, HTTPError
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def check_mobile_friendly(website: str, api_key: str) -> str:
    """
    Check if the given website is mobile-friendly using the Google Mobile-Friendly Test API.

    Args:
        website (str): The URL of the website to be checked.
        api_key (str): The API key for accessing the Google Mobile-Friendly Test API.

    Returns:
        str: 
            - "🟢" if the website is mobile-friendly.
            - "🔴" if the website is not mobile-friendly.
            - "⚪" for any errors.
    """
    # Input validation and URL normalization
    if not website or not api_key:
        logger.error("Website URL and API key are required")
        return "⚪"
    
    # Normalize URL
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"
    
    try:
        parsed_url = urlparse(website)
        if not parsed_url.netloc:
            logger.error(f"Invalid URL format: {website}")
            return "⚪"
    except Exception as e:
        logger.error(f"URL parsing error for {website}: {e}")
        return "⚪"

    api_url = f"https://searchconsole.googleapis.com/v1/urlTestingTools/mobileFriendlyTest:run?key={api_key}"
    payload = {"url": website}
    headers = {'Content-Type': 'application/json'}

    try:
        # Make a POST request to the Google API
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        # Parse the response JSON
        result = response.json()

        # Enhanced detection patterns
        mobile_friendliness = result.get('mobileFriendliness', '').upper()
        
        if mobile_friendliness == 'MOBILE_FRIENDLY':
            logger.info(f"Website {website} is mobile-friendly")
            return "🟢"
        elif mobile_friendliness == 'NOT_MOBILE_FRIENDLY':
            logger.warning(f"Website {website} is not mobile-friendly")
            return "🔴"
        else:
            logger.error(f"Unexpected mobile friendliness status: {mobile_friendliness}")
            return "⚪"

    except requests.HTTPError as e:
        if e.response.status_code == 429:
            logger.error(f"API rate limit exceeded for {website}")
        elif e.response.status_code == 403:
            logger.error(f"API key invalid or insufficient permissions for {website}")
        else:
            logger.error(f"HTTP error {e.response.status_code} while checking {website}: {e}")
        return "⚪"
    except requests.RequestException as e:
        logger.error(f"Request error while checking mobile-friendliness for {website}: {e}")
        return "⚪"
    except (KeyError, json.JSONDecodeError) as e:
        logger.error(f"Invalid API response format for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error while checking mobile-friendliness for {website}: {e}")
        return "⚪"
