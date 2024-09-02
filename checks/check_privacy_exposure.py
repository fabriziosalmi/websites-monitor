import re
import requests
from requests.exceptions import RequestException, Timeout, HTTPError
from bs4 import BeautifulSoup

def check_privacy_exposure(website):
    """
    Check a given website for potential exposure of sensitive or private data.
    
    Args:
    - website (str): The URL of the website to be checked.
    
    Returns:
    - str: "🟢" if no patterns of sensitive data are found, "🔴" otherwise, "⚪" if an error occurred.
    """
    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Patterns to detect sensitive data exposure
    sensitive_data_patterns = [
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',  # Email addresses
        r'\b\d{10}\b',  # 10-digit numbers (e.g., phone numbers)
        r'(\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b)',  # Credit Card numbers
        r'(\b\d{3}[- ]?\d{2}[- ]?\d{4}\b)',  # Social Security Numbers
        r'("AWS_ACCESS_KEY_ID"|"aws_secret_access_key"|"AKIA[0-9A-Z]{16}")',  # AWS Access Keys
        r'("-----BEGIN PRIVATE KEY-----")',  # Private key exposure
    ]

    try:
        # Method 1: Direct HTML content analysis
        response = requests.get(website, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP issues

        # Check for sensitive data patterns in the HTML content
        if any(re.search(pattern, response.text, re.IGNORECASE) for pattern in sensitive_data_patterns):
            return "🔴"

        # Method 2: Meta tags and scripts analysis
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Check meta tags for privacy leaks
        meta_tags = soup.find_all('meta', {'name': re.compile(r'(description|keywords|author)', re.IGNORECASE)})
        for tag in meta_tags:
            content = tag.get('content', '')
            if any(re.search(pattern, content, re.IGNORECASE) for pattern in sensitive_data_patterns):
                return "🔴"

        # Method 3: Check for accidental exposure of environment variables or configuration files
        common_files = [
            '/.env', '/config.json', '/settings.py', '/config.php', 
            '/wp-config.php', '/.git/config', '/.htaccess', '/.aws/credentials'
        ]

        # Attempt to access known sensitive paths
        for path in common_files:
            try:
                file_response = requests.get(f"{website}{path}", headers=headers, timeout=5)
                if file_response.status_code == 200 and any(re.search(pattern, file_response.text, re.IGNORECASE) for pattern in sensitive_data_patterns):
                    return "🔴"
            except (Timeout, HTTPError):
                continue  # Ignore timeouts and HTTP errors for these paths

        return "🟢"

    except (Timeout, HTTPError) as e:
        print(f"Timeout or HTTP error occurred while checking privacy exposure for {website}: {e}")
        return "⚪"
    except RequestException as e:
        print(f"Request-related error occurred while checking privacy exposure for {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking privacy exposure for {website}: {e}")
        return "⚪"
