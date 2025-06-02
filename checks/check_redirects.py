import requests
import logging
from requests.exceptions import RequestException, Timeout, HTTPError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_redirects(website: str) -> str:
    """
    Verify if a website using HTTP redirects to its HTTPS counterpart with enhanced security analysis.

    Args:
        website (str): The URL (without protocol) of the website to check.

    Returns:
        str:
            - "🟢" if the site redirects from HTTP to HTTPS securely.
            - "🟠" if redirect exists but has minor security issues.
            - "🔴" if it does not redirect from HTTP to HTTPS or has security issues.
            - "⚪" in case of an error.
    """
    # Input validation and URL normalization
    if not website or not isinstance(website, str):
        logger.error(f"Invalid website input: {website}")
        return "⚪"
    
    website = website.strip()
    if website.startswith(('http://', 'https://')):
        from urllib.parse import urlparse
        parsed = urlparse(website)
        website = parsed.netloc

    headers = {
        "User-Agent": "HTTPtoHTTPSRedirectChecker/2.0"
    }

    try:
        # Make an HTTP request to the site and prevent automatic redirects
        response = requests.get(f"http://{website}", headers=headers, allow_redirects=False, timeout=15)
        redirect_location = response.headers.get('Location', '')

        # Enhanced redirect analysis
        if response.status_code in [301, 302, 303, 307, 308] and redirect_location:
            logger.debug(f"Redirect detected: {response.status_code} -> {redirect_location}")
            
            # Check if redirect is to HTTPS
            if redirect_location.startswith(f"https://{website}"):
                # Check for permanent redirect (301, 308) - more secure
                if response.status_code in [301, 308]:
                    logger.info(f"Website {website} has secure permanent redirect to HTTPS")
                    return "🟢"
                else:
                    logger.info(f"Website {website} redirects to HTTPS but uses temporary redirect")
                    return "🟠"
            elif redirect_location.startswith('https://'):
                # Redirects to HTTPS but different domain
                logger.warning(f"Website {website} redirects to different HTTPS domain: {redirect_location}")
                return "🟠"
            else:
                # Redirects but not to HTTPS
                logger.warning(f"Website {website} redirects but not to HTTPS: {redirect_location}")
                return "🔴"
        else:
            # No redirect or invalid redirect
            logger.warning(f"Website {website} does not redirect from HTTP to HTTPS")
            return "🔴"

    except (Timeout, HTTPError) as e:
        logger.warning(f"HTTP/Timeout error while checking redirects for {website}: {e}")
        return "⚪"
    except RequestException as e:
        logger.warning(f"Request error while checking redirects for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error while checking redirects for {website}: {e}")
        return "⚪"
