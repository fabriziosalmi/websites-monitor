import re
import logging
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, HTTPError
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Declarations like "width: 1200px" (not max-width/min-width) of at least this
# many pixels force a desktop-sized layout: 980px is the width mobile browsers
# assume for pages without a responsive viewport.
FIXED_WIDTH_THRESHOLD_PX = 980
FIXED_WIDTH_CSS = re.compile(r'(?<![-\w])width\s*:\s*(\d+(?:\.\d+)?)px', re.IGNORECASE)


def _parse_viewport(content: str) -> dict:
    """Parse a viewport meta content string into a dict of lowercase keys/values."""
    directives = {}
    for part in re.split(r'[,;]', content or ''):
        if '=' in part:
            key, value = part.split('=', 1)
            directives[key.strip().lower()] = value.strip().lower()
    return directives


def check_mobile_friendly(website: str, api_key: str = None) -> str:
    """
    Check if the given website is mobile-friendly from its HTML.

    This used to call Google's Mobile-Friendly Test API, which needs a Search
    Console API key the monitor never passes and whose retirement Google
    announced for December 2023. It is now a local static check of the page
    HTML. It does not render the page: it only reads markup and inline CSS.

    Criteria:
        1. A <meta name="viewport"> exists and its content has
           width=device-width. Without it mobile browsers render the page at a
           desktop width (about 980px) and shrink it: 🔴.
        2. The viewport does not disable zooming (user-scalable=no or
           maximum-scale below 2): otherwise 🟡.
        3. No fixed-width layout hints: no "width: Npx" declaration with
           N >= 980 in <style> blocks or style attributes (max-width and
           min-width are ignored), and no width="N" attribute with N >= 980:
           otherwise 🟡.

    Args:
        website (str): The URL or bare domain of the website to be checked.
        api_key (str, optional): Ignored, kept for backward compatibility.

    Returns:
        str:
            - "🟢" if all criteria pass.
            - "🟡 (reasons)" if the viewport is responsive but there are issues.
            - "🔴 (no responsive viewport meta)" if criterion 1 fails.
            - "⚪" for any errors.
    """
    # Input validation and URL normalization
    if not website or not isinstance(website, str):
        logger.error("Website URL is required")
        return "⚪"

    # Normalize URL
    website = website.strip()
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

    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/124.0 Mobile Safari/537.36'
    }

    try:
        response = requests.get(website, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Responsive viewport
        viewport = soup.find('meta', attrs={'name': re.compile(r'^viewport$', re.IGNORECASE)})
        directives = _parse_viewport(viewport.get('content', '') if viewport else '')
        if directives.get('width') != 'device-width':
            logger.warning(f"Website {website} has no responsive viewport meta")
            return "🔴 (no responsive viewport meta)"

        issues = []

        # 2. Zoom must not be disabled
        max_scale = directives.get('maximum-scale')
        try:
            zoom_capped = max_scale is not None and float(max_scale) < 2
        except ValueError:
            zoom_capped = False
        if directives.get('user-scalable') in ('no', '0') or zoom_capped:
            issues.append("zoom disabled")

        # 3. Fixed-width layout hints
        css_sources = [tag.get_text() for tag in soup.find_all('style')]
        css_sources += [tag['style'] for tag in soup.find_all(style=True)]
        fixed_css = [
            float(value)
            for css in css_sources
            for value in FIXED_WIDTH_CSS.findall(css)
            if float(value) >= FIXED_WIDTH_THRESHOLD_PX
        ]
        fixed_attrs = [
            tag for tag in soup.find_all(width=True)
            if str(tag['width']).strip().isdigit() and int(tag['width']) >= FIXED_WIDTH_THRESHOLD_PX
        ]
        if fixed_css or fixed_attrs:
            issues.append(f"{len(fixed_css) + len(fixed_attrs)} fixed-width element(s) >= {FIXED_WIDTH_THRESHOLD_PX}px")

        if issues:
            logger.warning(f"Website {website} mobile issues: {', '.join(issues)}")
            return f"🟡 ({', '.join(issues)})"

        logger.info(f"Website {website} is mobile-friendly")
        return "🟢"

    except HTTPError as e:
        logger.error(f"HTTP error {e.response.status_code} while checking {website}: {e}")
        return "⚪"
    except RequestException as e:
        logger.error(f"Request error while checking mobile-friendliness for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error while checking mobile-friendliness for {website}: {e}")
        return "⚪"
