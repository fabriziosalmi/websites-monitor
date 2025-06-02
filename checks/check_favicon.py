import requests
import logging
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, HTTPError
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)

def check_favicon(website: str) -> str:
    """
    Check if the website has a valid favicon.

    Args:
        website (str): URL of the website to be checked.

    Returns:
        str: 
            - "🟢" if a valid favicon is found.
            - "🔴" if no valid favicon is found.
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
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    except Exception as e:
        logger.error(f"URL parsing error for {website}: {e}")
        return "⚪"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    }

    def check_favicon_url(url):
        """Helper function to check if a favicon URL is valid"""
        try:
            response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
            return response.status_code == 200
        except:
            try:
                response = requests.get(url, headers=headers, timeout=10, stream=True)
                return response.status_code == 200 and len(response.content) > 0
            except:
                return False

    try:
        # Enhanced detection patterns - multiple fallback mechanisms
        favicon_candidates = []
        
        # 1. Check default favicon.ico location
        default_favicon = f"{base_url}/favicon.ico"
        if check_favicon_url(default_favicon):
            logger.info(f"Favicon found at default location: {default_favicon}")
            return "🟢"
        favicon_candidates.append(default_favicon)

        # 2. Parse HTML for favicon references
        try:
            response = requests.get(website, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for various favicon link types
            favicon_rels = ['icon', 'shortcut icon', 'apple-touch-icon', 'apple-touch-icon-precomposed']
            
            for rel in favicon_rels:
                icons = soup.find_all('link', rel=lambda x: x and rel in x.lower() if x else False)
                for icon in icons:
                    href = icon.get('href')
                    if not href:
                        continue
                    
                    # Normalize URL
                    if href.startswith('//'):
                        favicon_url = f"{parsed_url.scheme}:{href}"
                    elif href.startswith('/'):
                        favicon_url = f"{base_url}{href}"
                    elif not href.startswith(('http://', 'https://')):
                        favicon_url = urljoin(website, href)
                    else:
                        favicon_url = href
                    
                    favicon_candidates.append(favicon_url)
                    
                    if check_favicon_url(favicon_url):
                        logger.info(f"Favicon found via HTML link tag: {favicon_url}")
                        return "🟢"

        except Exception as e:
            logger.warning(f"Error parsing HTML for favicon on {website}: {e}")

        # 3. Try common alternative locations
        common_paths = ['/apple-touch-icon.png', '/icon.png', '/favicon.png']
        for path in common_paths:
            favicon_url = f"{base_url}{path}"
            favicon_candidates.append(favicon_url)
            if check_favicon_url(favicon_url):
                logger.info(f"Favicon found at common location: {favicon_url}")
                return "🟢"

        logger.warning(f"No valid favicon found for {website}. Checked {len(set(favicon_candidates))} locations")
        return "🔴"
        
    except (HTTPError, RequestException) as e:
        logger.error(f"Request error while checking favicon for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error while checking favicon for {website}: {e}")
        return "⚪"
