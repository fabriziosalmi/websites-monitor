import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from requests.exceptions import RequestException, Timeout, HTTPError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_sitemap(website):
    """
    Check if the provided website has a sitemap.xml with enhanced validation.

    Args:
        website (str): The URL of the website to be checked.

    Returns:
        str: 
            - "🟢" if a valid sitemap is found.
            - "🔴" if no sitemap is found or if there's a request-related error.
            - "⚪" for any other unexpected errors.
    """
    # Input validation and URL normalization
    if not website or not isinstance(website, str):
        logger.error(f"Invalid website input: {website}")
        return "⚪"
    
    website = website.strip()
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"
    
    # Enhanced sitemap paths with more comprehensive patterns
    sitemap_paths = [
        '/sitemap.xml',                # Default location
        '/sitemap_index.xml',          # Index file for multiple sitemaps
        '/sitemap/sitemap.xml',        # Common alternative path
        '/sitemap1.xml',               # Numbered sitemap
        '/sitemap-index.xml',          # Alternative index naming
        '/sitemap/sitemap-index.xml',  # Nested alternative
        '/sitemap_index.xml.gz',       # Compressed sitemap
        '/sitemaps.xml',               # Plural variant
        '/site-map.xml',               # Hyphenated variant
        '/robots.txt'                  # Check robots.txt for sitemap reference
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        session = requests.Session()
        session.headers.update(headers)
        
        # Method 1: Check common sitemap paths
        for path in sitemap_paths[:-1]:  # Exclude robots.txt for now
            try:
                sitemap_url = urljoin(website, path)
                response = session.get(sitemap_url, timeout=15)
                
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # Enhanced validation of sitemap content
                    if any(indicator in content for indicator in ['<urlset', '<sitemapindex', '<url>', '<sitemap>']):
                        logger.info(f"Valid sitemap found at {sitemap_url}")
                        return "🟢"
                    
            except (Timeout, HTTPError, RequestException):
                continue
        
        # Method 2: Check robots.txt for sitemap references
        try:
            robots_url = urljoin(website, '/robots.txt')
            robots_response = session.get(robots_url, timeout=10)
            
            if robots_response.status_code == 200:
                robots_content = robots_response.text.lower()
                if 'sitemap:' in robots_content:
                    # Extract sitemap URLs from robots.txt
                    import re
                    sitemap_matches = re.findall(r'sitemap:\s*(.+)', robots_content, re.IGNORECASE)
                    
                    for sitemap_url in sitemap_matches:
                        sitemap_url = sitemap_url.strip()
                        try:
                            sitemap_response = session.get(sitemap_url, timeout=10)
                            if sitemap_response.status_code == 200:
                                content = sitemap_response.text.lower()
                                if any(indicator in content for indicator in ['<urlset', '<sitemapindex', '<url>', '<sitemap>']):
                                    logger.info(f"Valid sitemap found via robots.txt: {sitemap_url}")
                                    return "🟢"
                        except (Timeout, HTTPError, RequestException):
                            continue
        except (Timeout, HTTPError, RequestException):
            pass
        
        # Method 3: Check HTML for sitemap links
        try:
            main_response = session.get(website, timeout=15)
            if main_response.status_code == 200:
                soup = BeautifulSoup(main_response.text, 'html.parser')
                
                # Look for sitemap links in HTML
                sitemap_links = soup.find_all('a', href=lambda x: x and 'sitemap' in x.lower())
                for link in sitemap_links:
                    href = link.get('href')
                    if href:
                        sitemap_url = urljoin(website, href)
                        try:
                            sitemap_response = session.get(sitemap_url, timeout=10)
                            if sitemap_response.status_code == 200:
                                content = sitemap_response.text.lower()
                                if any(indicator in content for indicator in ['<urlset', '<sitemapindex']):
                                    logger.info(f"Valid sitemap found in HTML links: {sitemap_url}")
                                    return "🟢"
                        except (Timeout, HTTPError, RequestException):
                            continue
        except (Timeout, HTTPError, RequestException):
            pass
        
        logger.warning(f"No valid sitemap found for {website}")
        return "🔴"
    
    except RequestException as e:
        logger.error(f"Request error while checking sitemap for {website}: {e}")
        return "🔴"
    except Exception as e:
        logger.error(f"Unexpected error while checking sitemap for {website}: {e}")
        return "⚪"
