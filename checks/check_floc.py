import requests
from requests.exceptions import RequestException, Timeout, HTTPError

def check_floc(website):
    """
    Check if the website has opted out of FLoC (Federated Learning of Cohorts).
    
    Args:
    - website (str): URL of the website to be checked.
    
    Returns:
    - str: "🟢" if the site has opted out of FLoC, "🔴" if it has not, or "⚪" if an error occurred.
    """
    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    try:
        # Perform the HTTP request with timeout
        response = requests.get(website, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Fetch and check the 'Permissions-Policy' header
        permissions_policy = response.headers.get('Permissions-Policy', '').lower()
        if 'interest-cohort=()' in permissions_policy:
            return "🟢"
        return "🔴"

    except (Timeout, HTTPError) as e:
        # Handle timeout and HTTP errors specifically
        print(f"Timeout or HTTP error occurred while checking FLoC for {website}: {e}")
    except RequestException as e:
        # Handle all other requests-related exceptions
        print(f"An error occurred while checking FLoC for {website}: {e}")
    
    return "⚪"
