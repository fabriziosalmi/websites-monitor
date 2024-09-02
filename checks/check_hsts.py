import requests
from requests.exceptions import RequestException, Timeout, HTTPError

def check_hsts(website: str) -> str:
    """
    Check if the website implements HTTP Strict Transport Security (HSTS).

    Args:
        website (str): URL of the website to be checked.

    Returns:
        str: 
            - "🟢" if the site has HSTS enabled.
            - "🔴" if the site does not have HSTS enabled.
            - "⚪" if an error occurred during the check.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
    }

    try:
        # Make a request to the website
        response = requests.get(f"https://{website}", headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Check if the 'Strict-Transport-Security' header is present
        if 'Strict-Transport-Security' in response.headers:
            print(f"HSTS is enabled for {website}.")
            return "🟢"
        else:
            print(f"HSTS is not enabled for {website}.")
            return "🔴"
    
    except (Timeout, HTTPError) as e:
        print(f"Timeout or HTTP error occurred while checking HSTS for {website}: {e}")
        return "⚪"
    except RequestException as e:
        print(f"Request-related error occurred while checking HSTS for {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking HSTS for {website}: {e}")
        return "⚪"
