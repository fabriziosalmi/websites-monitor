import requests
import logging
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, HTTPError, Timeout

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_open_graph_protocol(website: str) -> str:
    """
    Check a given website for the presence of essential Open Graph Protocol meta tags with enhanced validation.

    Args:
        website (str): The URL of the website to be checked.

    Returns:
        str:
            - "🟢" if essential Open Graph Protocol meta tags are found.
            - "🔴" if essential Open Graph Protocol meta tags are missing.
            - "⚪" for any errors.
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
        # Make a request to the website
        response = requests.get(website, headers=headers, timeout=15)
        response.raise_for_status()

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # List of essential Open Graph tags
        essential_tags = {'og:title', 'og:type', 'og:image', 'og:url'}
        recommended_tags = {'og:description', 'og:site_name', 'og:locale'}

        # Extract all Open Graph meta tags
        meta_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))

        # Extract the properties of found meta tags
        found_tags = {tag['property'] for tag in meta_tags if tag.has_attr('property') and tag.get('content')}

        logger.info(f"Open Graph analysis for {website}: {len(found_tags)} tags found")
        logger.debug(f"Found OG tags: {found_tags}")

        # Check if all essential tags are present
        missing_essential = essential_tags - found_tags
        found_recommended = recommended_tags.intersection(found_tags)

        if not missing_essential:
            logger.info(f"All essential Open Graph tags found for {website}.")
            if len(found_recommended) >= 2:
                return "🟢"  # Has essential + recommended tags
            return "🟢"  # Has essential tags
        else:
            logger.warning(f"Missing essential Open Graph tags for {website}: {missing_essential}")
            return "🔴"
    
    except (Timeout, HTTPError, RequestException) as e:
        logger.warning(f"Request error occurred while checking Open Graph Protocol tags on {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"An unexpected error occurred while checking Open Graph Protocol tags on {website}: {e}")
        return "⚪"
