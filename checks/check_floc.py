import requests
import logging
from requests.exceptions import RequestException, Timeout, HTTPError
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def check_floc(website: str) -> str:
    """
    Check if the website has opted out of FLoC (Federated Learning of Cohorts).
    
    Args:
        website (str): URL of the website to be checked.
    
    Returns:
        str: 
            - "🟢" if the site has opted out of FLoC
            - "🔴" if it has not opted out
            - "⚪" if an error occurred
    """
    # Input validation and URL normalization
    if not website:
        logger.error("Website URL is required")
        return "⚪"
    
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

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    }

    try:
        # Perform the HTTP request with timeout
        response = requests.get(website, headers=headers, timeout=15)
        response.raise_for_status()

        # Enhanced detection patterns
        permissions_policy = response.headers.get('Permissions-Policy', '').lower()
        
        # Check for FLoC opt-out in Permissions-Policy header
        if 'interest-cohort=()' in permissions_policy:
            logger.info(f"FLoC opt-out detected via Permissions-Policy for {website}")
            return "🟢"
        
        # Fallback: Check for older Feature-Policy header
        feature_policy = response.headers.get('Feature-Policy', '').lower()
        if 'interest-cohort' in feature_policy and "'none'" in feature_policy:
            logger.info(f"FLoC opt-out detected via Feature-Policy for {website}")
            return "🟢"
        
        logger.warning(f"No FLoC opt-out detected for {website}")
        return "🔴"

    except (Timeout, HTTPError) as e:
        logger.error(f"HTTP error while checking FLoC for {website}: {e}")
        return "⚪"
    except RequestException as e:
        logger.error(f"Request error while checking FLoC for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error while checking FLoC for {website}: {e}")
        return "⚪"
