import requests
import logging
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, Timeout, HTTPError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_third_party_resources(website: str) -> str:
    """
    Check for third-party resources loaded by the website with enhanced analysis.

    Args:
        website (str): URL of the website to be checked.

    Returns:
        str:
            - "🟢" if the number of third-party resources is minimal (0-3 domains).
            - "🟠" if there is a moderate number of third-party resources (4-8 domains).
            - "🔴" if there is a high number of third-party resources (9+ domains).
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
        # Fetch content with proper error handling
        response = requests.get(website, headers=headers, timeout=15)
        response.raise_for_status()

        # Parse main domain
        main_domain = urlparse(website).netloc.lower()
        main_domain_parts = main_domain.split('.')
        if len(main_domain_parts) >= 2:
            root_domain = '.'.join(main_domain_parts[-2:])
        else:
            root_domain = main_domain

        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Track third-party domains and resource types
        third_party_domains = set()
        resource_types = {
            'scripts': 0,
            'stylesheets': 0,
            'images': 0,
            'fonts': 0,
            'other': 0
        }

        # Enhanced resource detection
        resource_selectors = [
            ('script', 'src', 'scripts'),
            ('link', 'href', 'stylesheets'),
            ('img', 'src', 'images'),
            ('source', 'src', 'images'),
            ('iframe', 'src', 'other'),
            ('embed', 'src', 'other'),
            ('object', 'data', 'other')
        ]

        for tag_name, attr_name, resource_type in resource_selectors:
            for tag in soup.find_all(tag_name):
                resource_url = tag.get(attr_name)
                if resource_url:
                    parsed_url = urlparse(resource_url)
                    domain = parsed_url.netloc.lower()
                    
                    if domain and domain != main_domain:
                        # Check if it's a subdomain of the main domain
                        domain_parts = domain.split('.')
                        if len(domain_parts) >= 2:
                            domain_root = '.'.join(domain_parts[-2:])
                            if domain_root != root_domain:
                                third_party_domains.add(domain)
                                resource_types[resource_type] += 1
                                logger.debug(f"Third-party {resource_type}: {resource_url}")

        # Check for font resources specifically
        for link in soup.find_all('link', rel=lambda x: x and 'font' in str(x).lower()):
            href = link.get('href')
            if href:
                parsed_url = urlparse(href)
                domain = parsed_url.netloc.lower()
                if domain and domain != main_domain:
                    domain_parts = domain.split('.')
                    if len(domain_parts) >= 2:
                        domain_root = '.'.join(domain_parts[-2:])
                        if domain_root != root_domain:
                            third_party_domains.add(domain)
                            resource_types['fonts'] += 1

        third_party_count = len(third_party_domains)
        total_resources = sum(resource_types.values())

        logger.info(f"Third-party analysis for {website}: {third_party_count} domains, {total_resources} resources")
        logger.debug(f"Resource breakdown: {resource_types}")
        logger.debug(f"Third-party domains: {list(third_party_domains)}")

        # Enhanced scoring based on domain count and resource distribution
        if third_party_count == 0:
            logger.info(f"No third-party resources detected for {website}")
            return "🟢"
        elif third_party_count <= 3:
            logger.info(f"Minimal third-party resources ({third_party_count} domains) for {website}")
            return "🟢"
        elif third_party_count <= 8:
            logger.warning(f"Moderate third-party resources ({third_party_count} domains) for {website}")
            return "🟠"
        else:
            logger.warning(f"High number of third-party resources ({third_party_count} domains) for {website}")
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
