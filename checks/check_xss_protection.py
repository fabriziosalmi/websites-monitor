import requests
import logging
from typing import Optional
from requests.exceptions import RequestException, Timeout, HTTPError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_xss_protection(website: str, timeout_seconds: Optional[int] = 10) -> str:
    """
    Check if the X-XSS-Protection header is present in the HTTP response headers of a website.

    Args:
        website (str): The URL of the website to be checked.
        timeout_seconds (int, optional): Timeout for the HTTP request in seconds. Default is 10 seconds.

    Returns:
        str:
            - "🟢" if X-XSS-Protection header is present and properly configured.
            - "🟠" if header is present but with suboptimal configuration.
            - "🔴" if X-XSS-Protection header is absent.
            - "⚪" for any errors or non-success HTTP responses.
    """
    # Input validation and URL normalization
    if not website or not isinstance(website, str):
        logger.error(f"Invalid website input: {website}")
        return "⚪"
    
    website = website.strip()
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Make request with proper timeout and error handling
        response = requests.get(website, headers=headers, timeout=timeout_seconds)
        response.raise_for_status()

        # Check X-XSS-Protection header
        xss_protection = response.headers.get('X-XSS-Protection', '').lower()
        
        if xss_protection:
            logger.info(f"X-XSS-Protection header found for {website}: {xss_protection}")
            
            # Enhanced validation of header value
            if '1; mode=block' in xss_protection:
                return "🟢"  # Optimal configuration
            elif xss_protection.startswith('1'):
                return "🟠"  # Present but not optimal
            else:
                return "🔴"  # Present but disabled (0)
        else:
            # Check for Content-Security-Policy as alternative protection
            csp_header = response.headers.get('Content-Security-Policy', '')
            if csp_header and 'unsafe-inline' not in csp_header.lower():
                logger.info(f"No X-XSS-Protection but CSP found for {website}")
                return "🟠"  # CSP provides some XSS protection
            
            logger.warning(f"X-XSS-Protection header missing for {website}")
            return "🔴"

    except Timeout:
        logger.warning(f"Timeout occurred while checking XSS protection for {website}")
        return "⚪"
    except HTTPError as e:
        logger.warning(f"HTTP error for {website}: {e}")
        return "⚪"
    except RequestException as e:
        logger.warning(f"Request error for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error for {website}: {e}")
        return "⚪"
