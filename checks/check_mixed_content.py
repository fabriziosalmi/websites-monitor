from bs4 import BeautifulSoup
import requests
import logging
from requests.exceptions import RequestException, HTTPError
from urllib.parse import urlparse, urljoin
import re

logger = logging.getLogger(__name__)

def check_mixed_content(website: str) -> str:
    """
    Check a given website for mixed content issues by searching for resources loaded over HTTP.

    Args:
        website (str): The URL of the website to be checked.

    Returns:
        str:
            - "🟢" if no mixed content is found.
            - "🔴" if mixed content is found.
            - "⚪" for any errors.
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Make a request to the website
        response = requests.get(website, headers=headers, timeout=15)
        response.raise_for_status()

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Enhanced detection patterns - check multiple attributes and elements
        mixed_content_found = []
        
        # Check src attributes (img, script, iframe, etc.)
        elements_with_src = soup.find_all(attrs={'src': True})
        for element in elements_with_src:
            src = element.get('src', '')
            if src.startswith('http://'):
                mixed_content_found.append(f"{element.name}[src]: {src}")
        
        # Check href attributes (link, a tags)
        elements_with_href = soup.find_all(attrs={'href': True})
        for element in elements_with_href:
            href = element.get('href', '')
            if href.startswith('http://') and element.name in ['link']:  # Focus on resource links
                mixed_content_found.append(f"{element.name}[href]: {href}")
        
        # Check CSS url() patterns in style attributes and tags
        style_elements = soup.find_all(['style']) + soup.find_all(attrs={'style': True})
        for element in style_elements:
            style_content = element.get('style', '') if element.has_attr('style') else element.get_text()
            if style_content:
                http_urls = re.findall(r'url\(["\']?(http://[^"\')\s]+)["\']?\)', style_content)
                for url in http_urls:
                    mixed_content_found.append(f"CSS url(): {url}")

        # Check if there is any mixed content
        if mixed_content_found:
            logger.warning(f"Mixed content found on {website}: {len(mixed_content_found)} instances")
            for content in mixed_content_found[:5]:  # Log first 5 instances
                logger.warning(f"  - {content}")
            return "🔴"
        else:
            logger.info(f"No mixed content found on {website}")
            return "🟢"

    except HTTPError as e:
        logger.error(f"HTTP error {e.response.status_code} while checking mixed content on {website}: {e}")
        return "⚪"
    except RequestException as e:
        logger.error(f"Request error while checking mixed content on {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error while checking mixed content on {website}: {e}")
        return "⚪"
