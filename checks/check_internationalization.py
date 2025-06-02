import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

logger = logging.getLogger(__name__)

def check_internationalization(website: str) -> str:
    """
    Checks if a website has implemented internationalization (i18n) using the lang attribute.

    Args:
        website (str): The URL of the website to check.

    Returns:
        str:
           - "🟢" if i18n is detected
           - "🟡" if partial i18n is detected
           - "⚪" if i18n is not detected or an error occurred.
    """
    # Input validation and URL normalization
    if not website:
        logger.error("Website URL is required")
        return "⚪"
    
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"
    
    try:
        parsed_url = urlparse(website)
        if not parsed_url.netloc:
            logger.error(f"Invalid URL format: {website}")
            return "⚪"
    except Exception as e:
        logger.error(f"URL parsing error for {website}: {e}")
        return "⚪"

    try:
        response = requests.get(website, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Enhanced detection patterns
        i18n_indicators = []
        
        # Check HTML lang attribute
        html_tag = soup.find("html")
        if html_tag and html_tag.has_attr("lang"):
            lang_value = html_tag.get("lang", "").strip()
            if lang_value and len(lang_value) >= 2:
                i18n_indicators.append(f"HTML lang attribute: {lang_value}")
        
        # Check for hreflang attributes in link tags
        hreflang_links = soup.find_all("link", attrs={"hreflang": True})
        if hreflang_links:
            i18n_indicators.append(f"hreflang links: {len(hreflang_links)} found")
        
        # Check for language-specific meta tags
        lang_meta = soup.find_all("meta", attrs={"http-equiv": "content-language"})
        if lang_meta:
            i18n_indicators.append("Content-Language meta tag found")
        
        # Check for common i18n URL patterns
        if re.search(r'/[a-z]{2}(?:-[A-Z]{2})?/', website):
            i18n_indicators.append("Language code in URL pattern")
        
        # Improved scoring and categorization
        if len(i18n_indicators) >= 2:
            logger.info(f"Strong internationalization detected for {website}: {', '.join(i18n_indicators)}")
            return "🟢"
        elif len(i18n_indicators) == 1:
            logger.info(f"Basic internationalization detected for {website}: {i18n_indicators[0]}")
            return "🟡"
        else:
            logger.info(f"No internationalization detected for {website}")
            return "⚪"

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error while checking internationalization for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error while checking internationalization for {website}: {e}")
        return "⚪"
