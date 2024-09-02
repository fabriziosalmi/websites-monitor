import re
import requests
from requests.exceptions import RequestException, Timeout, HTTPError
from bs4 import BeautifulSoup

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
    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        'User-Agent': 'AdTrackingChecker/1.0'
    }

    try:
        # Method 1: Direct HTML Content Analysis
        response = requests.get(website, headers=headers, timeout=10)
        response.raise_for_status()

        # Check for the presence of common ad/tracking scripts
        has_google_analytics = re.search(r'www\.google-analytics\.com/analytics\.js', response.text) is not None
        has_adsbygoogle = re.search(r'pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js', response.text) is not None

        # Additional ad/tracking services to check
        other_ad_tracking_scripts = [
            r'connect\.facebook\.net',   # Facebook Pixel
            r'cdn\.branch\.io',          # Branch Metrics
            r'pixel\.quantserve\.com',   # Quantcast Pixel
            r'bat\.bing\.com',           # Microsoft Advertising
            r'cdn\.taboola\.com',        # Taboola
            r'tracker\.cleverbridge\.com', # Cleverbridge
            r'googletagmanager\.com/gtag/js'  # Google Tag Manager
        ]

        has_other_ad_tracking = any(re.search(pattern, response.text) for pattern in other_ad_tracking_scripts)

        # Determine the return status based on the findings
        if has_google_analytics and has_adsbygoogle:
            return "🔴"
        elif has_google_analytics:
            return "🟠"
        elif has_other_ad_tracking:
            return "🟡"
        else:
            return "🟢"

    except (Timeout, HTTPError) as e:
        print(f"Timeout or HTTP error occurred while checking for ad network and tracking scripts for {website}: {e}")
        # Fallback to another method in case of errors

    except RequestException as e:
        print(f"Request-related error occurred while checking for ad network and tracking scripts for {website}: {e}")
        # Fallback to another method in case of errors

    try:
        # Method 2: Using BeautifulSoup for heuristic checks (fallback)
        soup = BeautifulSoup(response.text, 'lxml')

        # Check for presence of common script tags associated with tracking
        scripts = soup.find_all('script', src=True)
        for script in scripts:
            src = script.get('src', '')
            if 'google-analytics' in src or 'adsbygoogle' in src:
                return "🔴"
            elif any(re.search(pattern, src) for pattern in other_ad_tracking_scripts):
                return "🟡"

        # Check for inline tracking scripts (e.g., inline configuration of Google Analytics)
        inline_scripts = soup.find_all('script')
        for script in inline_scripts:
            if script.string and re.search(r'GoogleAnalyticsObject|gtag\(', script.string):
                return "🟠"

        return "🟢"

    except (Timeout, HTTPError, RequestException) as e:
        print(f"Error during BeautifulSoup heuristic check for {website}: {e}")

    except Exception as e:
        print(f"An unexpected error occurred while checking for ad network and tracking scripts for {website}: {e}")

    return "⚪"
