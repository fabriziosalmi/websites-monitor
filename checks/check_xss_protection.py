import requests
from typing import Optional

def check_xss_protection(website: str, timeout_seconds: Optional[int] = 5) -> str:
    """
    Check if the X-XSS-Protection header is present in the HTTP response headers of a website.

    Args:
    - website (str): The URL of the website to be checked.
    - timeout_seconds (int, optional): Timeout for the HTTP request in seconds. Default is 5 seconds.

    Returns:
    - str: "🟢" if X-XSS-Protection header is present, "🔴" otherwise, "⚪" for any errors.
    """
    try:
        response = requests.get(f"https://{website}", timeout=timeout_seconds)
        
        # Check if the response status code is in the 2xx range
        if 200 <= response.status_code < 300:
            if 'X-XSS-Protection' in response.headers:
                return "🟢"
            else:
                return "🔴"
        else:
            print(f"Received non-success HTTP status code: {response.status_code}")
            return "⚪"
    except requests.Timeout:
        print(f"Timeout occurred while checking XSS protection for {website}.")
        return "⚪"
    except Exception as e:
        print(f"An error occurred while checking XSS protection for {website}: {e}")
        return "⚪"
