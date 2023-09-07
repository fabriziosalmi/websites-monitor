import requests

def ensure_url_scheme(website):
    """
    Ensure the URL has an http or https scheme.
    
    Args:
    - website (str): URL of the website.

    Returns:
    - str: URL with https scheme.
    """
    if not website.startswith(('http://', 'https://')):
        return f'https://{website}'
    return website
    
def check_cookie_duration(website):
    """
    Ensure that session cookies set by the website don't have an overly long duration.
    Args:
    - website (str): URL of the website to be checked.
    
    Returns:
    - str: "🔴" if any cookie has an overly long duration, "🟢" otherwise, "🟡" for any errors.
    """
    try:
        response = requests.get(website)
        long_duration_cookies = 0
        for cookie in response.cookies:
            # Check if 'max-age' or 'expires' is set for the cookie
            if cookie.has_attr('max-age'):
                # Let's assume a session cookie with more than 7 days (604800 seconds) duration is too long.
                # Adjust this value as per your requirements.
                if int(cookie['max-age']) > 604800:
                    long_duration_cookies += 1
            elif cookie.has_attr('expires'):
                # If using 'expires', calculate the duration from the current time.
                # Remember to parse the 'expires' date and calculate the difference.
                # This is a placeholder. Actual implementation might need date parsing and calculation.
                pass

        if long_duration_cookies > 0:
            return "🔴"  # Cookies with long duration found
        return "🟢"  # All cookies have acceptable durations
    except Exception as e:
        print(f"Error checking cookie duration for {website}. Error: {e}")
        return "🟡"  # Error occurred
