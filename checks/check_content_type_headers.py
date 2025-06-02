import requests
from requests.exceptions import RequestException, Timeout, HTTPError

def check_content_type_headers(website):
    """
    Checks if the 'Content-Type' header of the website is set to 'text/html' 
    and has a character encoding specified.

    Args:
        website (str): The website URL to check.

    Returns:
        str: 
            - "🟢" if the header is properly set
            - "🔴" if the header is not properly set
            - "⚪" if an error occurs
    """
    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        'User-Agent': 'ContentTypeChecker/1.0'
    }

    try:
        # Method 1: Check Content-Type header directly
        response = requests.get(website, headers=headers, timeout=10)
        response.raise_for_status()
        content_type = response.headers.get('Content-Type', '')

        # Check for both 'text/html' and a character encoding
        if 'text/html' in content_type.lower() and 'charset=' in content_type.lower():
            print(f"Content-Type is correctly set for {website}.")
            return "🟢"
        else:
            print(f"Content-Type is not properly set for {website}.")
            return "🔴"

    except (Timeout, HTTPError, RequestException) as e:
        print(f"Request error occurred while checking Content-Type headers for {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking Content-Type headers for {website}: {e}")
        return "⚪"
