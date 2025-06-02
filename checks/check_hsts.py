import requests
import logging
from requests.exceptions import RequestException, Timeout, HTTPError
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def check_hsts(website: str) -> str:
    """
    Check if the website implements HTTP Strict Transport Security (HSTS).

    Args:
        website (str): URL of the website to be checked.

    Returns:
        str: 
            - "🟢" if the site has HSTS enabled with good configuration.
            - "🟡" if HSTS is enabled but with suboptimal configuration.
            - "🔴" if the site does not have HSTS enabled.
            - "⚪" if an error occurred during the check.
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
    }

    try:
        # Make a request to the website
        response = requests.get(website, headers=headers, timeout=15)
        response.raise_for_status()

        # Enhanced detection patterns
        hsts_header = response.headers.get('Strict-Transport-Security', '')
        
        if not hsts_header:
            logger.warning(f"No HSTS header found for {website}")
            return "🔴"
        
        # Improved scoring and categorization
        hsts_lower = hsts_header.lower()
        max_age_match = None
        
        # Extract max-age value
        import re
        max_age_pattern = re.search(r'max-age=(\d+)', hsts_lower)
        if max_age_pattern:
            max_age = int(max_age_pattern.group(1))
            
            # Check for security best practices
            has_include_subdomains = 'includesubdomains' in hsts_lower
            has_preload = 'preload' in hsts_lower
            
            # Categorize based on configuration quality
            if max_age >= 31536000 and has_include_subdomains:  # 1 year or more with subdomains
                logger.info(f"Strong HSTS configuration for {website}: max-age={max_age}, includeSubDomains={has_include_subdomains}, preload={has_preload}")
                return "🟢"
            elif max_age >= 86400:  # At least 1 day
                logger.info(f"Basic HSTS configuration for {website}: max-age={max_age}, includeSubDomains={has_include_subdomains}")
                return "🟡"
            else:
                logger.warning(f"Weak HSTS configuration for {website}: max-age too low ({max_age})")
                return "🟡"
        else:
            logger.warning(f"Invalid HSTS header format for {website}: {hsts_header}")
            return "🟡"

    except requests.RequestException as e:
        logger.error(f"Request error while checking HSTS for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error while checking HSTS for {website}: {e}")
        return "⚪"
