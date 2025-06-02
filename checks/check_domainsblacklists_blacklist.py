import requests
import logging
from requests.exceptions import RequestException, Timeout, HTTPError
from urllib.parse import urlparse
import re
import hashlib
import time

logger = logging.getLogger(__name__)

# Simple cache to avoid repeated downloads
_blacklist_cache = {
    'data': None,
    'timestamp': 0,
    'ttl': 3600  # Cache for 1 hour
}

def check_domainsblacklists_blacklist(domain: str) -> str:
    """
    Check if a domain is present in a large blacklist file hosted online.

    Args:
        domain (str): The domain to check against the blacklist.

    Returns:
        str: 
            - "🔴" if the domain is found in the blacklist
            - "🟢" if the domain is not found in the blacklist
            - "⚪" if an error occurs
    """
    # Input validation and normalization
    if not domain:
        logger.error("Domain is required")
        return "⚪"
    
    # Normalize domain
    domain = domain.lower().strip()
    domain = re.sub(r'^https?://', '', domain)
    domain = re.sub(r'^www\.', '', domain)
    domain = domain.split('/')[0]  # Remove path if present
    domain = domain.split(':')[0]  # Remove port if present
    
    # Validate domain format
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]$', domain):
        logger.error(f"Invalid domain format: {domain}")
        return "⚪"

    url = "https://github.com/fabriziosalmi/blacklists/releases/download/latest/blacklist.txt"
    
    headers = {
        'User-Agent': 'DomainBlacklistChecker/2.0',
        'Accept-Encoding': 'gzip, deflate'
    }

    try:
        # Check cache first for performance optimization
        current_time = time.time()
        if _blacklist_cache['data'] and (current_time - _blacklist_cache['timestamp'] < _blacklist_cache['ttl']):
            logger.debug("Using cached blacklist data")
            blacklist_set = _blacklist_cache['data']
        else:
            logger.info("Downloading fresh blacklist data")
            # Stream the response to handle large files efficiently
            response = requests.get(url, headers=headers, stream=True, timeout=60)
            response.raise_for_status()

            # Build a set for O(1) lookup performance
            blacklist_set = set()
            line_count = 0
            
            for line in response.iter_lines(decode_unicode=True):
                # Ensure line is a string and handle properly
                if line and isinstance(line, str):
                    if not line.startswith('#'):  # Skip comments
                        cleaned_line = line.strip().lower()
                        if cleaned_line:
                            blacklist_set.add(cleaned_line)
                            line_count += 1
                elif line and isinstance(line, bytes):
                    # Handle bytes if somehow we get them
                    line_str = line.decode('utf-8', errors='ignore')
                    if not line_str.startswith('#'):
                        cleaned_line = line_str.strip().lower()
                        if cleaned_line:
                            blacklist_set.add(cleaned_line)
                            line_count += 1
            
            # Update cache
            _blacklist_cache['data'] = blacklist_set
            _blacklist_cache['timestamp'] = current_time
            
            logger.info(f"Loaded {line_count} domains into blacklist")

        # Enhanced detection patterns - check domain and subdomains
        domains_to_check = [domain]
        
        # Add parent domains for subdomain checking
        parts = domain.split('.')
        for i in range(1, len(parts)):
            parent_domain = '.'.join(parts[i:])
            if len(parent_domain) > 3:  # Avoid checking TLDs
                domains_to_check.append(parent_domain)

        # Check all domain variants
        for check_domain in domains_to_check:
            if check_domain in blacklist_set:
                logger.warning(f"Domain {check_domain} found in blacklist (original: {domain})")
                return "🔴"

        logger.info(f"Domain {domain} not found in blacklist")
        return "🟢"

    except (Timeout, HTTPError) as e:
        logger.error(f"HTTP error while checking domain {domain} against blacklist: {e}")
        return "⚪"
    except RequestException as e:
        logger.error(f"Request error while checking domain {domain} against blacklist: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error while checking domain {domain} against blacklist: {e}")
        return "⚪"
