import requests
import logging
from requests.exceptions import RequestException, Timeout, HTTPError
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_redirect_chains(website: str) -> str:
    """
    Check the number of redirects that a website triggers with enhanced security analysis.

    Args:
        website (str): The URL of the website to check.

    Returns:
        str: 
            - "🟢" if no redirects or optimal redirect pattern.
            - "🟠" if there's one redirect or acceptable chain.
            - "🔴" if multiple redirects or security issues.
            - "⚪" in case of an error.
    """
    # Input validation and URL normalization
    if not website or not isinstance(website, str):
        logger.error(f"Invalid website input: {website}")
        return "⚪"
    
    website = website.strip()
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        "User-Agent": "RedirectChainChecker/2.0"
    }

    try:
        redirect_count = 0
        redirect_chain = []
        current_url = website
        visited_urls = set()
        max_redirects = 10  # Prevent infinite loops

        while redirect_count < max_redirects:
            # Prevent redirect loops
            if current_url in visited_urls:
                logger.warning(f"Redirect loop detected for {website}")
                return "🔴"
            
            visited_urls.add(current_url)
            response = requests.get(current_url, headers=headers, allow_redirects=False, timeout=15)
            
            # Check if there's a redirect
            if response.status_code in [301, 302, 303, 307, 308]:
                redirect_location = response.headers.get('location', '')
                if not redirect_location:
                    logger.warning(f"Empty redirect location for {current_url}")
                    break
                
                redirect_count += 1
                redirect_chain.append({
                    'from': current_url,
                    'to': redirect_location,
                    'status': response.status_code
                })
                
                # Handle relative URLs
                if not redirect_location.startswith(('http://', 'https://')):
                    redirect_location = urljoin(current_url, redirect_location)
                
                current_url = redirect_location
                logger.debug(f"Redirect {redirect_count}: {response.status_code} -> {redirect_location}")
            else:
                # No more redirects
                break

        logger.info(f"Redirect analysis for {website}: {redirect_count} redirects found")
        
        if redirect_chain:
            logger.debug(f"Redirect chain: {redirect_chain}")

        # Enhanced evaluation
        if redirect_count == 0:
            logger.info(f"No redirects found for {website}")
            return "🟢"
        elif redirect_count == 1:
            # Check if it's a good redirect (HTTP to HTTPS)
            if (redirect_chain[0]['from'].startswith('http://') and 
                redirect_chain[0]['to'].startswith('https://') and
                redirect_chain[0]['status'] in [301, 308]):
                logger.info(f"Single secure redirect found for {website}")
                return "🟢"
            else:
                logger.info(f"Single redirect found for {website}")
                return "🟠"
        elif redirect_count <= 3:
            logger.warning(f"Multiple redirects ({redirect_count}) detected for {website}")
            return "🟠"
        else:
            logger.warning(f"Excessive redirects ({redirect_count}) detected for {website}")
            return "🔴"

    except (Timeout, HTTPError) as e:
        logger.warning(f"HTTP/Timeout error while checking redirect chains for {website}: {e}")
        return "⚪"
    except RequestException as e:
        logger.warning(f"Request error while checking redirect chains for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error while checking redirect chains for {website}: {e}")
        return "⚪"
