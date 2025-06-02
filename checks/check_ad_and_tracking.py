import re
import requests
from requests.exceptions import RequestException, Timeout, HTTPError
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_ad_and_tracking(website):
    """
    Check if the website is using Google Analytics, AdsbyGoogle, or other common ad/tracking scripts.

    Args:
        website (str): URL of the website to be checked.

    Returns:
        str: 
            - "🔴" if both Google Analytics and AdsbyGoogle are present
            - "🟠" if only Google Analytics is present
            - "🟡" if other ad/tracking scripts are detected
            - "🟢" if neither are present
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

    # Enhanced ad/tracking services patterns
    tracking_patterns = {
        'google_analytics': [
            r'www\.google-analytics\.com/analytics\.js',
            r'www\.googletagmanager\.com/gtag/js',
            r'gtag\(',
            r'GoogleAnalyticsObject',
            r'ga\(',
        ],
        'google_ads': [
            r'pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js',
            r'googlesyndication\.com',
            r'adsbygoogle',
        ],
        'facebook': [
            r'connect\.facebook\.net',
            r'fbevents\.js',
            r'facebook\.com/tr',
        ],
        'other_tracking': [
            r'cdn\.branch\.io',
            r'pixel\.quantserve\.com',
            r'bat\.bing\.com',
            r'cdn\.taboola\.com',
            r'tracker\.cleverbridge\.com',
            r'hotjar\.com',
            r'fullstory\.com',
            r'mixpanel\.com',
            r'segment\.io',
            r'amplitude\.com',
        ]
    }

    try:
        # Enhanced content analysis with retry mechanism
        response = requests.get(website, headers=headers, timeout=15)
        response.raise_for_status()
        content = response.text.lower()

        # Score-based detection system
        detection_score = {
            'google_analytics': 0,
            'google_ads': 0,
            'facebook': 0,
            'other_tracking': 0
        }

        # Check patterns in content
        for category, patterns in tracking_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    detection_score[category] += 1
                    logger.debug(f"Found {category} pattern: {pattern}")

        # Enhanced BeautifulSoup analysis
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Check script tags
        scripts = soup.find_all('script', src=True)
        for script in scripts:
            src = script.get('src', '').lower()
            for category, patterns in tracking_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, src):
                        detection_score[category] += 1

        # Check inline scripts
        inline_scripts = soup.find_all('script')
        for script in inline_scripts:
            if script.string:
                script_content = script.string.lower()
                for category, patterns in tracking_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, script_content):
                            detection_score[category] += 1

        # Determine result based on weighted scoring
        has_google_analytics = detection_score['google_analytics'] > 0
        has_google_ads = detection_score['google_ads'] > 0
        has_other_tracking = (detection_score['facebook'] + detection_score['other_tracking']) > 0

        logger.info(f"Tracking detection scores for {website}: {detection_score}")

        if has_google_analytics and has_google_ads:
            return "🔴"
        elif has_google_analytics:
            return "🟠"
        elif has_other_tracking:
            return "🟡"
        else:
            return "🟢"

    except (Timeout, HTTPError, RequestException) as e:
        logger.warning(f"Request error for {website}: {e}")
        
        # Enhanced fallback with basic pattern matching
        try:
            response = requests.get(website, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Simple pattern matching as fallback
            content = response.text.lower()
            if any(pattern in content for patterns in tracking_patterns.values() for pattern in patterns[:2]):
                return "🟡"
            return "🟢"

        except Exception as e:
            logger.error(f"Fallback failed for {website}: {e}")
            return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error for {website}: {e}")
        return "⚪"
