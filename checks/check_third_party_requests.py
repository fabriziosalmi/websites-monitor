import requests
import logging
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, Timeout, HTTPError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_third_party_requests(website: str) -> str:
    """
    Monitor the number of third-party requests made by a website with enhanced analysis.

    Args:
        website (str): URL of the website to be checked.
    
    Returns:
        str: 
            - "🟢" if the number of third-party requests is minimal (0-20).
            - "🟠" if there is a moderate number of third-party requests (21-50).
            - "🔴" if the website makes a high number of third-party requests (51+).
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
        # Send HTTP GET request with enhanced error handling
        response = requests.get(website, headers=headers, timeout=15)
        response.raise_for_status()

        # Parse the main domain from the website URL
        parsed_url = urlparse(website)
        main_domain = parsed_url.netloc.lower()
        main_domain_parts = main_domain.split('.')
        if len(main_domain_parts) >= 2:
            root_domain = '.'.join(main_domain_parts[-2:])
        else:
            root_domain = main_domain

        # Parse HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'lxml')

        # Track third-party requests by category
        third_party_requests = 0
        request_categories = {
            'scripts': 0,
            'stylesheets': 0,
            'images': 0,
            'fonts': 0,
            'iframes': 0,
            'other': 0
        }
        
        third_party_domains = set()

        # Enhanced resource detection with categorization
        resource_selectors = [
            ('script', 'src', 'scripts'),
            ('link', 'href', 'stylesheets'),
            ('img', 'src', 'images'),
            ('source', 'src', 'images'),
            ('iframe', 'src', 'iframes'),
            ('embed', 'src', 'other'),
            ('object', 'data', 'other'),
            ('video', 'src', 'other'),
            ('audio', 'src', 'other')
        ]

        for tag_name, attr_name, category in resource_selectors:
            for tag in soup.find_all(tag_name):
                resource_url = tag.get(attr_name)
                if resource_url and resource_url.startswith(('http://', 'https://')):
                    parsed_resource = urlparse(resource_url)
                    domain = parsed_resource.netloc.lower()
                    
                    if domain and domain != main_domain:
                        # Check if it's a subdomain of the main domain
                        domain_parts = domain.split('.')
                        if len(domain_parts) >= 2:
                            domain_root = '.'.join(domain_parts[-2:])
                            if domain_root != root_domain:
                                third_party_requests += 1
                                third_party_domains.add(domain)
                                request_categories[category] += 1
                                logger.debug(f"Third-party {category}: {resource_url}")

        # Check for font resources specifically
        for link in soup.find_all('link', rel=lambda x: x and any(font_rel in str(x).lower() for font_rel in ['font', 'preload'])):
            href = link.get('href')
            if href and href.startswith(('http://', 'https://')):
                parsed_href = urlparse(href)
                domain = parsed_href.netloc.lower()
                if domain and domain != main_domain:
                    domain_parts = domain.split('.')
                    if len(domain_parts) >= 2:
                        domain_root = '.'.join(domain_parts[-2:])
                        if domain_root != root_domain:
                            third_party_requests += 1
                            third_party_domains.add(domain)
                            request_categories['fonts'] += 1

        logger.info(f"Third-party analysis for {website}: {third_party_requests} requests across {len(third_party_domains)} domains")
        logger.debug(f"Request breakdown: {request_categories}")
        logger.debug(f"Third-party domains: {list(third_party_domains)}")

        # Enhanced threshold-based evaluation
        if third_party_requests <= 20:
            logger.info(f"Minimal third-party requests ({third_party_requests}) for {website}")
            return "🟢"
        elif third_party_requests <= 50:
            logger.warning(f"Moderate third-party requests ({third_party_requests}) for {website}")
            return "🟠"
        else:
            logger.warning(f"High number of third-party requests ({third_party_requests}) for {website}")
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
