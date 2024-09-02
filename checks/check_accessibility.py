import requests
from requests.exceptions import RequestException, Timeout, HTTPError

def check_accessibility(website):
    """
    Check the website's accessibility score using Lighthouse or similar services.
    
    Args:
    - website (str): URL of the website to be checked.
    
    Returns:
    - str: "🟢" if the accessibility score is high (0.9 to 1),
           "🟠" if the score is moderate (0.8 to 0.9),
           "🔴" if the score is low (less than 0.8),
           "⚪" for any errors.
    """
    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    LIGHTHOUSE_API_ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    WAVE_API_ENDPOINT = "https://wave.webaim.org/api/request"

    # Primary parameters for Lighthouse API
    lighthouse_params = {
        "url": website,
        "category": "accessibility",
        "strategy": "desktop"  # Could use "mobile" for mobile-based audits
    }

    headers = {
        'User-Agent': 'AccessibilityChecker/1.0'
    }

    try:
        # Method 1: Google Lighthouse API
        response = requests.get(LIGHTHOUSE_API_ENDPOINT, params=lighthouse_params, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP issues
        data = response.json()

        # Extract accessibility score from the Lighthouse API response
        score = data['lighthouseResult']['categories']['accessibility']['score']
        if score >= 0.9:
            return "🟢"
        elif 0.8 <= score < 0.9:
            return "🟠"
        else:
            return "🔴"

    except (Timeout, HTTPError, RequestException) as e:
        print(f"Error checking accessibility via Lighthouse for {website}: {e}")
        # Fallback to another method in case of errors

    try:
        # Method 2: WAVE API as a fallback
        wave_params = {
            "key": "YOUR_WAVE_API_KEY",  # Replace with a valid WAVE API key
            "url": website,
            "reporttype": "json"
        }

        wave_response = requests.get(WAVE_API_ENDPOINT, params=wave_params, headers=headers, timeout=10)
        wave_response.raise_for_status()
        wave_data = wave_response.json()

        # Check WAVE's accessibility error count
        errors_count = wave_data['categories']['error']['count']
        if errors_count == 0:
            return "🟢"  # No accessibility errors
        elif 1 <= errors_count <= 10:
            return "🟠"  # Few accessibility errors
        else:
            return "🔴"  # Many accessibility errors

    except (Timeout, HTTPError, RequestException) as e:
        print(f"Error checking accessibility via WAVE for {website}: {e}")
    
    try:
        # Method 3: Manual heuristic checks (fallback)
        response = requests.get(website, headers=headers, timeout=10)
        response.raise_for_status()
        content = response.text

        # Simple heuristics: Check for presence of common accessibility features
        has_alt_text = bool(re.search(r'<img [^>]*alt="[^"]*"', content, re.IGNORECASE))
        has_aria_roles = bool(re.search(r'role="[^"]*"', content, re.IGNORECASE))
        has_language_attr = bool(re.search(r'<html[^>]* lang="[^"]*"', content, re.IGNORECASE))

        # Combine heuristic checks for a basic score
        if has_alt_text and has_aria_roles and has_language_attr:
            return "🟢"
        elif has_alt_text or has_aria_roles or has_language_attr:
            return "🟠"
        else:
            return "🔴"

    except (Timeout, HTTPError, RequestException) as e:
        print(f"Error during manual heuristic accessibility check for {website}: {e}")

    except Exception as e:
        print(f"An unexpected error occurred while checking accessibility for {website}: {e}")

    return "⚪"
