from bs4 import BeautifulSoup
from bs4 import FeatureNotFound

def check_amp_compatibility(html_content):
    """
    Check if the provided HTML content has AMP compatibility.

    Returns:
        "🟢" if AMP compatible
        "🔴" if not AMP compatible
    """
    try:
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
    
    except (FeatureNotFound, Exception) as e:
        print(f"An error occurred while checking AMP compatibility: {e}")
        return "🔴"
