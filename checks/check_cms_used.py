import logging
import re

import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Evidence is looked for in three places only: the URLs of the page's own
# assets and links, the generator meta tag, and the response headers. The
# old check searched the whole HTML for substrings, so "mage/" matched
# "image/png" (Magento on any site with a PNG favicon) and "wp-" matched any
# word starting with it (WordPress on github.com).
ASSET_PATTERNS = {
    "WordPress": [r"/wp-content/", r"/wp-includes/", r"/wp-json/"],
    "Drupal": [r"/sites/(default|all)/(files|modules|themes)/", r"/core/misc/drupal\.js"],
    "Joomla": [r"/media/(jui|system)/js/", r"index\.php\?option=com_", r"/components/com_"],
    "Wix": [r"static\.wixstatic\.com", r"static\.parastorage\.com"],
    "Squarespace": [r"static1\.squarespace\.com", r"squarespace-cdn\.com"],
    "Shopify": [r"cdn\.shopify\.com", r"/cdn/shop/"],
    "Magento": [r"/static/version\d+/", r"/skin/frontend/", r"/js/mage/"],
    "Ghost": [r"/ghost/api/", r"/public/ghost-sdk"],
}
HEADER_PATTERNS = {
    "Drupal": [("x-generator", r"drupal"), ("x-drupal-cache", r".")],
    "Wix": [("x-wix-request-id", r".")],
    "Shopify": [("x-shopid", r"."), ("x-shopify-stage", r".")],
    "Magento": [("x-magento-cache-debug", r"."), ("x-magento-tags", r".")],
    "WordPress": [("x-pingback", r"xmlrpc\.php"), ("link", r"/wp-json/")],
}
URL_ATTRIBUTES = ("src", "href", "data-src", "action")


def detect_cms(html: str, headers) -> str:
    """The CMS the page, its asset URLs or its headers name, or "" if none."""
    lowered = {k.lower(): v for k, v in (headers or {}).items()}
    for cms, rules in HEADER_PATTERNS.items():
        for header, pattern in rules:
            if header in lowered and re.search(pattern, lowered[header], re.I):
                return cms

    soup = BeautifulSoup(html, "html.parser")
    generator = soup.find("meta", attrs={"name": re.compile("^generator$", re.I)})
    if generator and generator.get("content"):
        content = generator["content"].lower()
        for cms in ASSET_PATTERNS:
            if cms.lower() in content:
                return cms

    urls = "\n".join(
        tag.get(attr)
        for tag in soup.find_all(True)
        for attr in URL_ATTRIBUTES
        if isinstance(tag.get(attr), str)
    )
    for cms, patterns in ASSET_PATTERNS.items():
        if any(re.search(p, urls, re.I) for p in patterns):
            return cms
    return ""


def check_cms_used(website):
    """
    Checks which CMS (if any) a website runs, from the URLs of its assets,
    its generator meta tag and its response headers.

    Args:
        website (str): The domain or URL to check.

    Returns:
        str:
            - "🟢 (CMS Name)" if a CMS is detected
            - "⚪ (no CMS detected)" if none is: not running a known CMS is
              not a fault, so this is no verdict
            - "⚪" if the page could not be fetched
    """
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    try:
        response = requests.get(website, headers={'User-Agent': 'CMSChecker/1.0'}, timeout=10)
        response.raise_for_status()
        cms = detect_cms(response.text, response.headers)
        if cms:
            logger.info(f"Detected CMS {cms} for {website}")
            return f"🟢 ({cms})"
        logger.info(f"No CMS detected for {website}")
        return "⚪ (no CMS detected)"
    except RequestException as e:
        logger.warning(f"Request error while checking CMS for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error while checking CMS for {website}: {e}")
        return "⚪"
