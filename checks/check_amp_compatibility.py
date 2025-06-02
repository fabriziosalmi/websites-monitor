import requests
from requests.exceptions import RequestException, Timeout, HTTPError
from bs4 import BeautifulSoup
from bs4 import FeatureNotFound

def check_amp_compatibility(website):
    """
    Check if the website has AMP compatibility.

    Args:
        website (str): URL of the website to be checked.

    Returns:
        str: "🟢" if AMP compatible, "🔴" if not AMP compatible, "⚪" if error occurs
    """
    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        'User-Agent': 'AMPChecker/1.0'
    }

    try:
        response = requests.get(website, headers=headers, timeout=10)
        response.raise_for_status()
        html_content = response.text

        # Prefer lxml parser for better performance, fallback to html.parser
        try:
            soup = BeautifulSoup(html_content, 'lxml')
        except FeatureNotFound:
            soup = BeautifulSoup(html_content, 'html.parser')

        # Check for AMP attributes on <html> tag
        amp_html = soup.find('html', attrs=lambda x: x and ('⚡' in x or 'amp' in x))
        
        # Check for required AMP script
        amp_script = soup.find('script', src="https://cdn.ampproject.org/v0.js")

        # Check for AMP-specific components like link to AMP version
        amp_link = soup.find('link', rel="amphtml")

        # Validate AMP criteria
        if html_content.lower().startswith('<!doctype html>') and (amp_html or amp_link) and amp_script:
            return "🟢"

        return "🔴"
    
    except (Timeout, HTTPError, RequestException) as e:
        print(f"Request error occurred while checking AMP compatibility for {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An error occurred while checking AMP compatibility for {website}: {e}")
        return "⚪"
