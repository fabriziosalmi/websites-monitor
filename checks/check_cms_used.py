import requests
from requests.exceptions import RequestException, Timeout, HTTPError
from bs4 import BeautifulSoup

def check_cms_used(website):
    """
    Checks which CMS (if any) is used by a website based on certain telltale patterns in its content.
    
    Args:
        website (str): The website URL to check.
    
    Returns:
        str: 
            - "🟢 (CMS Name)" if a CMS is detected
            - "🔴" if no CMS is detected
            - "⚪" if an error occurs
    """
    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        'User-Agent': 'CMSChecker/1.0'
    }

    cms_patterns = {
        "WordPress": ["wp-", "wp-content", "wp-includes", "wp-json", "xmlrpc.php"],
        "Drupal": ["Drupal", "sites/default/files", "drupal.js"],
        "Joomla": ["Joomla", "/templates/joomla/", "index.php?option=com_"],
        "Wix": ["wix.com", "wix-public", "wixstatic"],
        "Squarespace": ["squarespace.com", "static.squarespace.com"],
        "Shopify": ["shopify", "cdn.shopify.com"],
        "Magento": ["Magento", "mage/", "static/version", "skin/frontend"]
    }

    try:
        # Method 1: Direct HTML content analysis
        response = requests.get(website, headers=headers, timeout=10)
        response.raise_for_status()
        content = response.text

        # Search for CMS-specific patterns in the website content
        for cms, patterns in cms_patterns.items():
            if any(pattern in content for pattern in patterns):
                print(f"Detected CMS: {cms} for {website}.")
                return f"🟢 ({cms})"
        
        # Method 2: Additional heuristic checks with BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # Check for meta tags or generator information that might indicate a CMS
        meta_generator = soup.find('meta', attrs={'name': 'generator'})
        if meta_generator and meta_generator.get('content'):
            generator_content = meta_generator['content'].lower()
            for cms in cms_patterns:
                if cms.lower() in generator_content:
                    print(f"Detected CMS via meta tag: {cms} for {website}.")
                    return f"🟢 ({cms})"
        
        print(f"No CMS detected for {website}.")
        return "🔴"

    except (Timeout, HTTPError, RequestException) as e:
        print(f"Request error occurred while checking CMS for {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking CMS for {website}: {e}")
        return "⚪"
