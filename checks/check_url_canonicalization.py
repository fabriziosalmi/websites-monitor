import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, urlunparse
from requests.exceptions import RequestException, Timeout, HTTPError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_url_canonicalization(website: str) -> str:
    """
    Check if the given website uses a canonical link element to avoid potential duplicate content issues.
    
    Args:
        website (str): The URL of the website to be checked.
    
    Returns:
        str: 
            - "🟢" if a correct canonical link element is found.
            - "🟠" if canonical link exists but has minor issues.
            - "🔴" if no canonical link or major issues found.
            - "⚪" on errors.
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
        # Make request with proper error handling
        response = requests.get(website, headers=headers, timeout=15)
        response.raise_for_status()

        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        canonical_tags = soup.find_all('link', {'rel': 'canonical'})

        if not canonical_tags:
            logger.warning(f"No canonical link found for {website}")
            return "🔴"
        
        if len(canonical_tags) > 1:
            logger.warning(f"Multiple canonical links found for {website}")
            return "🟠"  # Multiple canonicals can be problematic

        canonical_tag = canonical_tags[0]
        canonical_href = canonical_tag.get('href')

        if not canonical_href:
            logger.warning(f"Empty canonical href for {website}")
            return "🔴"

        # Normalize URLs for comparison
        def normalize_url(url):
            parsed = urlparse(url)
            # Remove fragment, normalize path
            normalized = urlunparse((
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                parsed.path.rstrip('/') or '/',
                parsed.params,
                parsed.query,
                ''  # Remove fragment
            ))
            return normalized

        # Handle relative canonical URLs
        if canonical_href.startswith(('http://', 'https://')):
            canonical_url = canonical_href
        else:
            canonical_url = urljoin(website, canonical_href)

        normalized_website = normalize_url(website)
        normalized_canonical = normalize_url(canonical_url)

        logger.info(f"Canonical analysis for {website}: canonical={canonical_url}")

        # Enhanced validation
        if normalized_canonical == normalized_website:
            logger.info(f"Perfect canonical match for {website}")
            return "🟢"
        
        # Check if canonical points to a valid variation (e.g., with/without www)
        website_parsed = urlparse(normalized_website)
        canonical_parsed = urlparse(normalized_canonical)
        
        if (website_parsed.netloc.replace('www.', '') == canonical_parsed.netloc.replace('www.', '') and
            website_parsed.path == canonical_parsed.path):
            logger.info(f"Canonical points to valid domain variation for {website}")
            return "🟢"
        
        # Check if it's the same domain but different path (might be intentional)
        if website_parsed.netloc == canonical_parsed.netloc:
            logger.warning(f"Canonical points to different path on same domain for {website}")
            return "🟠"
        
        logger.warning(f"Canonical points to different domain for {website}")
        return "🔴"

    except (Timeout, HTTPError) as e:
        logger.warning(f"HTTP/Timeout error for {website}: {e}")
        return "⚪"
    except RequestException as e:
        logger.warning(f"Request error for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error for {website}: {e}")
        return "⚪"
