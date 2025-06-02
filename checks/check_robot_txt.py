import requests
import logging
from requests.exceptions import RequestException, Timeout, HTTPError
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_robot_txt(website):
    """
    Verify the presence and basic validity of a robots.txt file on a website.
    
    Args:
    - website (str): The URL (without protocol) of the website to check.
    
    Returns:
    - str: "🟢" if the site has a valid robots.txt file, "🔴" otherwise, and 
           "⚪" in case of an error.
    """
    # Input validation and URL normalization
    if not website or not isinstance(website, str):
        logger.error(f"Invalid website input: {website}")
        return "⚪"
    
    website = website.strip()
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        # Perform the HTTP request with a timeout
        robots_url = urljoin(website, '/robots.txt')
        response = requests.get(robots_url, headers=headers, timeout=15)
        response.raise_for_status()

        # Enhanced validation of robots.txt content
        content = response.text.lower()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        # Check for essential robots.txt directives
        has_user_agent = any(line.startswith('user-agent:') for line in lines)
        has_disallow = any(line.startswith('disallow:') for line in lines)
        has_allow = any(line.startswith('allow:') for line in lines)
        has_sitemap = any(line.startswith('sitemap:') for line in lines)
        
        # Additional validation checks
        valid_directives = {'user-agent:', 'disallow:', 'allow:', 'crawl-delay:', 'sitemap:', 'host:'}
        unknown_directives = []
        
        for line in lines:
            if ':' in line and not line.startswith('#'):
                directive = line.split(':')[0] + ':'
                if directive not in valid_directives:
                    unknown_directives.append(directive)

        # Scoring system for robots.txt quality
        score = 0
        if has_user_agent:
            score += 2
        if has_disallow or has_allow:
            score += 2
        if has_sitemap:
            score += 1
        if not unknown_directives:
            score += 1

        logger.info(f"Robots.txt analysis for {website}: score {score}/6, sitemaps: {has_sitemap}")
        
        if unknown_directives:
            logger.warning(f"Unknown directives found: {unknown_directives}")

        if score >= 4:
            logger.info(f"Valid and comprehensive robots.txt found for {website}")
            return "🟢"
        elif score >= 2:
            logger.info(f"Basic robots.txt found for {website}")
            return "🟢"
        else:
            logger.warning(f"Poor quality robots.txt found for {website}")
            return "🔴"
    
    except (Timeout, HTTPError) as e:
        logger.warning(f"HTTP/Timeout error while checking robots.txt for {website}: {e}")
        return "⚪"
    except RequestException as e:
        logger.warning(f"Request error while checking robots.txt for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error while checking robots.txt for {website}: {e}")
        return "⚪"
