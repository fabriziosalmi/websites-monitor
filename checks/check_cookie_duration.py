import requests
from datetime import datetime

def check_cookie_duration(website):
    """
    Ensure that session cookies set by the website don't have an overly long duration.
    
    Args:
    - website (str): URL of the website to be checked.
    
    Returns:
    - str: "🔴" if any cookie has an overly long duration, "🟢" otherwise, "🟡" for any errors.
    """
    try:
        response = requests.get(f"https://{website}")
        long_duration_cookies = 0
        
        for cookie in response.cookies:
            # Check if 'max-age' attribute exists for the cookie
            if cookie.has_attr('max-age'):
                # Let's assume a session cookie with more than 7 days (604800 seconds) duration is too long.
                if int(cookie['max-age']) > 604800:
                    long_duration_cookies += 1
            # Check if 'expires' attribute exists for the cookie
            elif cookie.has_attr('expires'):
                # Parse the 'expires' date and calculate the difference from the current time
                expires_datetime = datetime.strptime(cookie['expires'], "%a, %d-%b-%Y %H:%M:%S %Z")
                delta = expires_datetime - datetime.utcnow()
                if delta.total_seconds() > 604800:
                    long_duration_cookies += 1

        # Return based on the count of long-duration cookies
        if long_duration_cookies > 0:
            print(f"Found {long_duration_cookies} cookies with long duration on {website}.")
            return "🔴"
        return "🟢"
    except Exception as e:
        print(f"Error checking cookie duration for {website}. Error: {e}")
        return "🟡"
