import requests

def check_cors_headers(website):
    """
    Checks the CORS policy of the given website.
    
    Args:
    - website (str): The website URL to check.
    
    Returns:
    - str: "🟢" if the CORS policy is not a wildcard,
           "🔴" if the CORS policy is a wildcard or an error occurred during the check,
           "⚪" if an unexpected error occurred.
    """
    try:
        response = requests.options(f"https://{website}")
        cors_header = response.headers.get('Access-Control-Allow-Origin', 'None')

        # Handling multiple origins
        allowed_origins = [origin.strip() for origin in cors_header.split(",")]

        if '*' in allowed_origins:
            print(f"{website} has a wildcard CORS policy.")
            return "🔴"
        return "🟢"

    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred while checking CORS headers for {website}: {req_err}")
        return "🔴"
    except Exception as e:
        print(f"Unexpected error occurred while checking CORS headers for {website}: {e}")
        return "⚪"
