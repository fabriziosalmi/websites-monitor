import requests
from requests.exceptions import RequestException, HTTPError

def check_cors_headers(website: str) -> str:
    """
    Checks the CORS policy of the given website.

    Args:
        website (str): The website URL to check.

    Returns:
        str: 
            - "🟢" if the CORS policy is not a wildcard.
            - "🔴" if the CORS policy is a wildcard or if a request error occurred.
            - "⚪" if an unexpected error occurred.
    """
    headers = {
        'User-Agent': 'CORSPolicyChecker/1.0'
    }

    try:
        # Send an OPTIONS request to the website to check CORS headers
        response = requests.options(f"https://{website}", headers=headers, timeout=10)
        response.raise_for_status()

        # Get the 'Access-Control-Allow-Origin' header from the response
        cors_header = response.headers.get('Access-Control-Allow-Origin', 'None')

        if cors_header == '*':
            print(f"{website} has a wildcard CORS policy (Access-Control-Allow-Origin: *).")
            return "🔴"
        elif cors_header == 'None':
            print(f"{website} does not specify CORS policy (Access-Control-Allow-Origin header missing).")
            return "🔴"
        else:
            print(f"{website} has a restrictive CORS policy (Access-Control-Allow-Origin: {cors_header}).")
            return "🟢"

    except (HTTPError, RequestException) as req_err:
        print(f"HTTP or request error occurred while checking CORS headers for {website}: {req_err}")
        return "🔴"
    except Exception as e:
        print(f"Unexpected error occurred while checking CORS headers for {website}: {e}")
        return "⚪"
