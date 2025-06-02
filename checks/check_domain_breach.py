import requests
import logging
from requests.exceptions import RequestException, HTTPError
from urllib.parse import urlparse
import json
import re
import time

logger = logging.getLogger(__name__)

# Simple rate limiting cache
_rate_limit_cache = {
    'last_request': 0,
    'min_interval': 1.5  # Respect HIBP rate limits
}

def check_domain_breach(website: str) -> str:
    """
    Check if a domain has been found in any known data breaches using the Have I Been Pwned API.

    Args:
        website (str): The domain name to be checked.

    Returns:
        str:
            - "🟢" if no breaches are found.
            - "🟡" if the domain is found in old/resolved breaches.
            - "🔴" if the domain is found in recent/active breaches.
            - "⚪" if any errors occurred or if the breach check could not be completed.
    """
    # Input validation and normalization
    if not website:
        logger.error("Website URL is required")
        return "⚪"
    
    # Normalize domain
    website = website.lower().strip()
    website = re.sub(r'^https?://', '', website)
    website = re.sub(r'^www\.', '', website)
    website = website.split('/')[0]  # Remove path if present
    website = website.split(':')[0]  # Remove port if present
    
    # Validate domain format
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]$', website):
        logger.error(f"Invalid domain format: {website}")
        return "⚪"

    # Performance optimization - rate limiting
    current_time = time.time()
    time_since_last = current_time - _rate_limit_cache['last_request']
    if time_since_last < _rate_limit_cache['min_interval']:
        time.sleep(_rate_limit_cache['min_interval'] - time_since_last)
    
    _rate_limit_cache['last_request'] = time.time()

    try:
        # Enhanced API usage - check breaches endpoint
        url = f"https://haveibeenpwned.com/api/v3/breaches"
        headers = {
            "hibp-api-version": "3",
            "User-Agent": "WebsiteMonitor/1.0"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        if response.status_code == 200:
            all_breaches = response.json()
            
            # Enhanced detection patterns - check for domain-related breaches
            domain_breaches = []
            recent_breaches = []
            
            for breach in all_breaches:
                breach_domain = breach.get('Domain', '')
                breach_name = breach.get('Name', '').lower()
                breach_date = breach.get('BreachDate', '')
                
                # Check if breach is related to the domain
                if (website in breach_domain.lower() or 
                    website in breach_name or 
                    breach_domain.lower().endswith(website)):
                    
                    domain_breaches.append(breach)
                    
                    # Check if breach is recent (within last 2 years)
                    try:
                        from datetime import datetime
                        breach_datetime = datetime.strptime(breach_date, '%Y-%m-%d')
                        days_ago = (datetime.now() - breach_datetime).days
                        if days_ago <= 730:  # 2 years
                            recent_breaches.append(breach)
                    except:
                        pass
            
            # Improved scoring and categorization
            if recent_breaches:
                logger.critical(f"Domain {website} found in {len(recent_breaches)} recent breaches")
                for breach in recent_breaches[:3]:  # Log first 3 recent breaches
                    logger.critical(f"  - {breach.get('Name')} ({breach.get('BreachDate')}): {breach.get('Description', '')[:100]}...")
                return "🔴"
            elif domain_breaches:
                logger.warning(f"Domain {website} found in {len(domain_breaches)} older breaches")
                for breach in domain_breaches[:2]:  # Log first 2 older breaches
                    logger.warning(f"  - {breach.get('Name')} ({breach.get('BreachDate')})")
                return "🟡"
            else:
                logger.info(f"Domain {website} not found in any known breaches")
                return "🟢"
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            logger.error(f"API authentication failed for {website} - API key may be required")
        elif e.response.status_code == 429:
            logger.error(f"Rate limit exceeded while checking breaches for {website}")
        elif e.response.status_code == 404:
            logger.info(f"No breach data found for {website}")
            return "🟢"
        else:
            logger.error(f"HTTP error {e.response.status_code} while checking breaches for {website}: {e}")
        return "⚪"
    except RequestException as e:
        logger.error(f"Request error while checking breaches for {website}: {e}")
        return "⚪"
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON response while checking breaches for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error while checking breaches for {website}: {e}")
        return "⚪"
