import requests
import logging
from urllib.parse import urlparse
from requests.exceptions import RequestException, Timeout, HTTPError
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_subdomain_enumeration(website: str) -> tuple:
    """
    Check for the existence of common subdomains for a given website with enhanced security analysis.

    Args:
        website (str): The main domain of the website to be checked.

    Returns:
        tuple: A status symbol and a list of discovered subdomains.
            - "🟢" if no potentially risky subdomains were discovered.
            - "🟠" if some subdomains were found but appear safe.
            - "🔴" if risky subdomains were found.
            - "⚪" for unexpected errors.
    """
    # Input validation and URL normalization
    if not website or not isinstance(website, str):
        logger.error(f"Invalid website input: {website}")
        return "⚪", []
    
    # Extract domain from URL if full URL provided
    if website.startswith(('http://', 'https://')):
        parsed = urlparse(website)
        domain = parsed.netloc
    else:
        domain = website.strip()

    # Enhanced subdomain list with security-focused subdomains
    SUBDOMAINS = [
        # Common subdomains
        "www", "api", "dev", "test", "staging", "mail", "blog", "shop", "admin",
        # Development/staging subdomains (potentially risky)
        "development", "stage", "beta", "alpha", "demo", "sandbox",
        # Infrastructure subdomains
        "cdn", "static", "assets", "media", "files",
        # Potentially sensitive subdomains
        "backup", "old", "legacy", "archive", "temp", "tmp",
        # Service subdomains
        "ftp", "ssh", "vpn", "remote", "portal"
    ]
    
    # Categorize subdomains by risk level
    RISKY_SUBDOMAINS = {
        "dev", "test", "staging", "development", "stage", "beta", "alpha", 
        "demo", "sandbox", "backup", "old", "legacy", "archive", "temp", "tmp"
    }

    discovered_subdomains = []
    risky_subdomains = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    def check_subdomain(subdomain):
        """Helper function to check individual subdomain."""
        subdomain_url = f"https://{subdomain}.{domain}"
        try:
            response = requests.get(subdomain_url, headers=headers, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                logger.debug(f"Discovered subdomain: {subdomain_url}")
                return subdomain_url, subdomain in RISKY_SUBDOMAINS
            return None, False
        except (Timeout, HTTPError, RequestException):
            return None, False
        except Exception as e:
            logger.debug(f"Error checking {subdomain_url}: {e}")
            return None, False

    try:
        # Use ThreadPoolExecutor for concurrent subdomain checking
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit all subdomain checks
            future_to_subdomain = {
                executor.submit(check_subdomain, sub): sub 
                for sub in SUBDOMAINS
            }
            
            # Process results as they complete
            for future in as_completed(future_to_subdomain, timeout=60):
                subdomain = future_to_subdomain[future]
                try:
                    result, is_risky = future.result()
                    if result:
                        discovered_subdomains.append(result)
                        if is_risky:
                            risky_subdomains.append(result)
                except Exception as e:
                    logger.debug(f"Error processing result for {subdomain}: {e}")
                    continue

        # Enhanced result analysis
        total_discovered = len(discovered_subdomains)
        total_risky = len(risky_subdomains)

        logger.info(f"Subdomain enumeration for {domain}: {total_discovered} discovered, {total_risky} potentially risky")
        
        if total_risky > 0:
            logger.warning(f"Risky subdomains found: {risky_subdomains}")
            return "🔴", discovered_subdomains
        elif total_discovered > 5:
            logger.warning(f"Multiple subdomains discovered for {domain}, potential attack surface")
            return "🟠", discovered_subdomains
        elif total_discovered > 0:
            logger.info(f"Few subdomains discovered for {domain}")
            return "🟠", discovered_subdomains
        else:
            logger.info(f"No subdomains discovered for {domain}")
            return "🟢", []

    except Exception as e:
        logger.error(f"Unexpected error during subdomain enumeration for {domain}: {e}")
        return "⚪", []
