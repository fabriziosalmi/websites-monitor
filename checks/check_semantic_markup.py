import requests
import logging
from bs4 import BeautifulSoup
from bs4 import FeatureNotFound
from requests.exceptions import RequestException
import json
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_semantic_markup(website):
    """
    Check if the website contains semantic markup in the form of JSON-LD, Microdata, or RDFa.

    Args:
        website (str): The URL of the website to be checked.

    Returns:
        str: 
            - "🟢" if comprehensive semantic markup is found
            - "🟠" if some semantic markup is found
            - "🔴" if no semantic markup is found
            - "⚪" if an error occurs
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

    try:
        # Fetch website content
        response = requests.get(website, headers=headers, timeout=15)
        response.raise_for_status()
        html_content = response.text

        # Parse HTML content
        try:
            soup = BeautifulSoup(html_content, 'lxml')
        except FeatureNotFound:
            soup = BeautifulSoup(html_content, 'html.parser')
        
        markup_score = 0
        markup_types = []

        # Method 1: Check for JSON-LD semantic markup
        json_ld_scripts = soup.find_all('script', type="application/ld+json")
        if json_ld_scripts:
            valid_json_ld = 0
            for script in json_ld_scripts:
                try:
                    json_data = json.loads(script.string or '{}')
                    if json_data and '@context' in json_data:
                        valid_json_ld += 1
                        logger.debug(f"Valid JSON-LD found: {json_data.get('@type', 'Unknown type')}")
                except (json.JSONDecodeError, AttributeError):
                    continue
            
            if valid_json_ld > 0:
                markup_score += 3  # JSON-LD gets highest score
                markup_types.append(f"JSON-LD ({valid_json_ld} items)")

        # Method 2: Check for Microdata semantic markup
        microdata_elements = soup.find_all(attrs={"itemscope": True})
        if microdata_elements:
            microdata_with_type = [elem for elem in microdata_elements if elem.get('itemtype')]
            if microdata_with_type:
                markup_score += 2
                markup_types.append(f"Microdata ({len(microdata_with_type)} items)")

        # Method 3: Check for RDFa semantic markup
        rdfa_vocab = soup.find_all(attrs={"vocab": True})
        rdfa_typeof = soup.find_all(attrs={"typeof": True})
        rdfa_property = soup.find_all(attrs={"property": True})
        
        if rdfa_vocab or rdfa_typeof or rdfa_property:
            markup_score += 1
            rdfa_count = len(rdfa_vocab) + len(rdfa_typeof) + len(rdfa_property)
            markup_types.append(f"RDFa ({rdfa_count} attributes)")

        # Method 4: Check for Open Graph and Twitter Card markup
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
        
        if og_tags:
            markup_score += 1
            markup_types.append(f"Open Graph ({len(og_tags)} tags)")
        
        if twitter_tags:
            markup_score += 1
            markup_types.append(f"Twitter Cards ({len(twitter_tags)} tags)")

        # Method 5: Check for Schema.org patterns in class names
        schema_classes = soup.find_all(class_=re.compile(r'schema|hcard|vcard|geo|adr', re.IGNORECASE))
        if schema_classes:
            markup_score += 1
            markup_types.append(f"Schema classes ({len(schema_classes)} elements)")

        logger.info(f"Semantic markup analysis for {website}: Score {markup_score}, Types: {', '.join(markup_types)}")

        # Determine result based on markup score and types
        if markup_score >= 4:
            return "🟢"  # Comprehensive semantic markup
        elif markup_score >= 2:
            return "🟠"  # Some semantic markup
        else:
            return "🔴"  # No or minimal semantic markup

    except RequestException as e:
        logger.warning(f"Request error for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error for {website}: {e}")
        return "⚪"
