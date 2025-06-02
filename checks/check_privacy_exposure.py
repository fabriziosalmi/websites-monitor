import re
import requests
import logging
from requests.exceptions import RequestException, Timeout, HTTPError
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_privacy_exposure(website: str) -> str:
    """
    Check a given website for potential exposure of sensitive or private data with enhanced detection.
    
    Args:
        website (str): The URL of the website to be checked.
    
    Returns:
        str: "🟢" if no patterns of sensitive data are found, "🔴" otherwise, "⚪" if an error occurred.
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

    # Enhanced patterns to detect sensitive data exposure
    sensitive_data_patterns = [
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',  # Email addresses
        r'\b\d{10,11}\b',  # Phone numbers (10-11 digits)
        r'(\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b)',  # Credit Card numbers
        r'(\b\d{3}[- ]?\d{2}[- ]?\d{4}\b)',  # Social Security Numbers
        r'("AWS_ACCESS_KEY_ID"|"aws_secret_access_key"|"AKIA[0-9A-Z]{16}")',  # AWS Access Keys
        r'("-----BEGIN PRIVATE KEY-----")',  # Private key exposure
        r'("api_key"|"apikey"):\s*["\'][^"\']+["\']',  # API keys
        r'("password"|"passwd"):\s*["\'][^"\']+["\']',  # Passwords
        r'("secret"|"token"):\s*["\'][^"\']+["\']',  # Secrets/tokens
        r'\b[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\b',  # IP addresses
    ]

    exposure_score = 0

    try:
        # Method 1: Direct HTML content analysis
        response = requests.get(website, headers=headers, timeout=15)
        response.raise_for_status()

        # Check for sensitive data patterns in the HTML content
        for pattern in sensitive_data_patterns:
            matches = re.findall(pattern, response.text, re.IGNORECASE)
            if matches:
                exposure_score += len(matches)
                logger.warning(f"Sensitive data pattern found: {pattern[:30]}... ({len(matches)} matches)")

        # Method 2: Meta tags and scripts analysis
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check meta tags for privacy leaks
        meta_tags = soup.find_all('meta', {'name': re.compile(r'(description|keywords|author)', re.IGNORECASE)})
        for tag in meta_tags:
            content = tag.get('content', '')
            for pattern in sensitive_data_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    exposure_score += 1
                    logger.warning(f"Sensitive data in meta tag: {tag}")

        # Check script tags for exposed data
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string:
                for pattern in sensitive_data_patterns:
                    matches = re.findall(pattern, script.string, re.IGNORECASE)
                    if matches:
                        exposure_score += len(matches)
                        logger.warning(f"Sensitive data in script tag: {len(matches)} matches")

        # Method 3: Check for accidental exposure of configuration files
        sensitive_paths = [
            '/.env', '/config.json', '/settings.py', '/config.php', 
            '/wp-config.php', '/.git/config', '/.htaccess', '/.aws/credentials',
            '/database.yml', '/.env.local', '/.env.production', '/secrets.json',
            '/app.config', '/web.config', '/.npmrc', '/.dockerenv'
        ]

        for path in sensitive_paths:
            try:
                file_url = urljoin(website, path)
                file_response = requests.get(file_url, headers=headers, timeout=5)
                
                if file_response.status_code == 200:
                    for pattern in sensitive_data_patterns:
                        matches = re.findall(pattern, file_response.text, re.IGNORECASE)
                        if matches:
                            exposure_score += len(matches) * 2  # Higher weight for config files
                            logger.error(f"Sensitive data in config file {path}: {len(matches)} matches")
                            
            except (Timeout, HTTPError):
                continue  # Ignore timeouts and HTTP errors for these paths

        # Method 4: Check common backup/temp file patterns
        backup_patterns = [
            '/backup.sql', '/dump.sql', '/database.bak', '/site.zip',
            '/backup.zip', '/old_site.tar.gz', '/backup.tar'
        ]
        
        for backup_path in backup_patterns:
            try:
                backup_url = urljoin(website, backup_path)
                backup_response = requests.get(backup_url, headers=headers, timeout=5)
                
                if backup_response.status_code == 200:
                    exposure_score += 5  # High weight for accessible backup files
                    logger.error(f"Accessible backup file found: {backup_path}")
                    
            except (Timeout, HTTPError):
                continue

        logger.info(f"Privacy exposure analysis for {website}: exposure score {exposure_score}")

        if exposure_score == 0:
            return "🟢"
        else:
            logger.warning(f"Privacy exposure detected for {website}: score {exposure_score}")
            return "🔴"

    except (Timeout, HTTPError) as e:
        logger.warning(f"HTTP/Timeout error while checking privacy exposure for {website}: {e}")
        return "⚪"
    except RequestException as e:
        logger.warning(f"Request error while checking privacy exposure for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error while checking privacy exposure for {website}: {e}")
        return "⚪"
