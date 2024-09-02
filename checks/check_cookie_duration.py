import requests
from datetime import datetime
from requests.exceptions import RequestException, Timeout, HTTPError

def check_cookie_duration(website):
    """
    Ensure that session cookies set by the website don't have an overly long duration.
    
    Args:
        website (str): URL of the website to be checked.
    
    Returns:
        str: 
            - "🔴" if any cookie has an overly long duration
            - "🟢" if all cookies have an acceptable duration
            - "⚪" if an error occurs
    """
    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        'User-Agent': 'CookieDurationChecker/1.0'
    }

    try:
        # Perform the request to get cookies
        response = requests.get(website, headers=headers, timeout=10)
        response.raise_for_status()

        long_duration_cookies = 0
        max_duration_seconds = 604800  # 7 days in seconds

        for cookie in response.cookies:
            # Check if 'max-age' attribute exists for the cookie
            max_age = cookie.get('max-age')
            if max_age and int(max_age) > max_duration_seconds:
                long_duration_cookies += 1
                continue

            # Check if 'expires' attribute exists for the cookie
            expires = cookie.get('expires')
            if expires:
                try:
                    # Parse the 'expires' date and calculate the difference from the current time
                    expires_datetime = datetime.strptime(expires, "%a, %d-%b-%Y %H:%M:%S %Z")
                    delta = expires_datetime - datetime.utcnow()
                    if delta.total_seconds() > max_duration_seconds:
                        long_duration_cookies += 1
                except ValueError as e:
                    print(f"Error parsing the expiration date of a cookie: {e}")

        # Return based on the count of long-duration cookies
        if long_duration_cookies > 0:
            print(f"Found {long_duration_cookies} cookies with long duration on {website}.")
            return "🔴"
        print(f"All cookies have an acceptable duration on {website}.")
        return "🟢"

    except (Timeout, HTTPError) as e:
        print(f"Timeout or HTTP error occurred while checking cookie duration for {website}: {e}")
        return "⚪"
    except RequestException as e:
        print(f"Request-related error occurred while checking cookie duration for {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking cookie duration for {website}: {e}")
        return "⚪"
