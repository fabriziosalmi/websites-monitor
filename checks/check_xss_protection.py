import requests
from typing import Optional
from requests.exceptions import RequestException, Timeout, HTTPError

def check_xss_protection(website: str, timeout_seconds: Optional[int] = 5) -> str:
    """
    Check if the X-XSS-Protection header is present in the HTTP response headers of a website.

    Args:
        website (str): The URL of the website to be checked.
        timeout_seconds (int, optional): Timeout for the HTTP request in seconds. Default is 5 seconds.

    Returns:
        str:
            - "🟢" if X-XSS-Protection header is present.
            - "🔴" if X-XSS-Protection header is absent.
            - "⚪" for any errors or non-success HTTP responses.
    """
    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        'User-Agent': 'XSSProtectionChecker/1.0'
    }

    try:
        # Make a request to the website
        response = requests.get(website, headers=headers, timeout=timeout_seconds)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Check if the X-XSS-Protection header is present
        if 'X-XSS-Protection' in response.headers:
            print(f"'X-XSS-Protection' header is present for {website}.")
            return "🟢"
        else:
            print(f"'X-XSS-Protection' header is missing for {website}.")
            return "🔴"

    except Timeout:
        print(f"Timeout occurred while checking XSS protection for {website}.")
        return "⚪"
    except HTTPError as e:
        print(f"HTTP error occurred while checking XSS protection for {website}: {e}")
        return "⚪"
    except RequestException as e:
        print(f"Request-related error occurred while checking XSS protection for {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking XSS protection for {website}: {e}")
        return "⚪"
