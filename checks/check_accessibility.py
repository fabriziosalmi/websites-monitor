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
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    LIGHTHOUSE_API_ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    WAVE_API_ENDPOINT = "https://wave.webaim.org/api/request"

    lighthouse_params = {
        "url": website,
        "category": "accessibility",
        "strategy": "desktop"
    }

    headers = {'User-Agent': 'AccessibilityChecker/1.0'}

    try:
        response = requests.get(LIGHTHOUSE_API_ENDPOINT, params=lighthouse_params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        score = data['lighthouseResult']['categories']['accessibility']['score']
        if score >= 0.9:
            return "🟢"
        elif 0.8 <= score < 0.9:
            return "🟠"
        else:
            return "🔴"

    except (Timeout, HTTPError, RequestException):
        wave_params = {
            "key": "YOUR_WAVE_API_KEY",
            "url": website,
            "reporttype": "json"
        }
        try:
            wave_response = requests.get(WAVE_API_ENDPOINT, params=wave_params, headers=headers, timeout=10)
            wave_response.raise_for_status()
            wave_data = wave_response.json()
            errors_count = wave_data['categories']['error']['count']
            if errors_count == 0:
                return "🟢"
            elif 1 <= errors_count <= 10:
                return "🟠"
            else:
                return "🔴"

        except (Timeout, HTTPError, RequestException):
            try:
                response = requests.get(website, headers=headers, timeout=10)
                response.raise_for_status()
                content = response.text

                has_alt_text = bool(ALT_TEXT_REGEX.search(content))
                has_aria_roles = bool(ARIA_ROLES_REGEX.search(content))
                has_language_attr = bool(LANGUAGE_ATTR_REGEX.search(content))

                if has_alt_text and has_aria_roles and has_language_attr:
                    return "🟢"
                elif has_alt_text or has_aria_roles or has_language_attr:
                    return "🟠"
                else:
                    return "🔴"

            except (Timeout, HTTPError, RequestException, Exception) as e:
                print(f"Error during manual heuristic accessibility check for {website}: {e}")

    return "⚪"
