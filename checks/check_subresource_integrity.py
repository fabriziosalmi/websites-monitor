import requests
import logging
from bs4 import BeautifulSoup
from typing import Tuple
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_subresource_integrity(website: str) -> Tuple[str, int]:
    """
    Check if the given website uses Subresource Integrity (SRI) by analyzing external resources.
    
    Args:
        website (str): The URL of the website to be analyzed.
    
    Returns:
        tuple: A status symbol and a count of external resources with SRI.
            - "🟢" if most external resources have SRI protection.
            - "🟠" if some external resources have SRI protection.
            - "🔴" if no or few external resources have SRI protection.
            - "⚪" if an error occurs.
    """
    # Input validation and URL normalization
    if not website or not isinstance(website, str):
        logger.error(f"Invalid website input: {website}")
        return "⚪", 0
    
    website = website.strip()
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Fetch website content
        response = requests.get(website, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'lxml')

        # Find all external resources that should have SRI
        external_resources = []
        sri_protected_resources = []

        # Check script tags with external sources
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src and (src.startswith(('http://', 'https://')) or src.startswith('//')):
                external_resources.append(('script', src))
                if script.get('integrity'):
                    sri_protected_resources.append(('script', src, script.get('integrity')))

        # Check link tags (stylesheets, fonts, etc.)
        for link in soup.find_all('link', href=True):
            href = link.get('href')
            rel = link.get('rel', [])
            if isinstance(rel, str):
                rel = [rel]
            
            # Focus on stylesheets and preload resources
            if href and (href.startswith(('http://', 'https://')) or href.startswith('//')) and \
               any(r in rel for r in ['stylesheet', 'preload']):
                external_resources.append(('link', href))
                if link.get('integrity'):
                    sri_protected_resources.append(('link', href, link.get('integrity')))

        total_external = len(external_resources)
        total_sri_protected = len(sri_protected_resources)

        logger.info(f"SRI analysis for {website}: {total_sri_protected}/{total_external} external resources have SRI")
        
        if total_sri_protected > 0:
            logger.debug(f"SRI-protected resources: {[r[1] for r in sri_protected_resources]}")

        # Determine result based on SRI coverage
        if total_external == 0:
            logger.info(f"No external resources found for {website}")
            return "🟢", 0
        
        sri_coverage = total_sri_protected / total_external
        
        if sri_coverage >= 0.8:  # 80% or more have SRI
            logger.info(f"Excellent SRI coverage ({sri_coverage:.1%}) for {website}")
            return "🟢", total_sri_protected
        elif sri_coverage >= 0.4:  # 40% or more have SRI
            logger.warning(f"Moderate SRI coverage ({sri_coverage:.1%}) for {website}")
            return "🟠", total_sri_protected
        else:  # Less than 40% have SRI
            logger.warning(f"Poor SRI coverage ({sri_coverage:.1%}) for {website}")
            return "🔴", total_sri_protected

    except RequestException as e:
        logger.warning(f"Request error for {website}: {e}")
        return "⚪", 0
    except Exception as e:
        logger.error(f"Unexpected error for {website}: {e}")
        return "⚪", 0
