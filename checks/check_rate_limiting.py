import requests
import time
from urllib.parse import urlparse, urlunparse

def normalize_url(website):
    """
    Normalize the website URL, ensuring it has a scheme.
    
    Args:
    - website (str): The URL of the website to normalize.
    
    Returns:
    - str: The normalized URL.
    """
    parsed_url = urlparse(website)
    if not parsed_url.scheme:
        normalized_url = urlunparse(('https', parsed_url.netloc, parsed_url.path, '', '', ''))
    else:
        normalized_url = website
    return normalized_url

def check_rate_limiting(website, num_requests=5, delay=0.5, user_agent="RateLimitChecker/1.0", verbose=True):
    """
    Check if a website implements rate limiting by sending multiple rapid requests.
    
    Args:
    - website (str): The URL of the website to check.
    - num_requests (int): Number of requests to send for testing.
    - delay (float): Delay in seconds between each request.
    - user_agent (str): Custom User-Agent string for the requests.
    - verbose (bool): If True, prints detailed output; otherwise, runs silently.
    
    Returns:
    - dict: A dictionary containing the results:
      - "status": str, "🟢 Rate limiting detected", "🔴 No rate limiting detected", or "⚪ Error occurred"
      - "status_codes": list of int, the HTTP status codes returned by the requests
      - "error": str, the error message if an exception occurred, otherwise None
    """
    headers = {
        "User-Agent": user_agent
    }
    
    # Normalize the URL
    try:
        website = normalize_url(website)
    except Exception as e:
        if verbose:
            print(f"Invalid URL format: {e}")
        return {"status": "⚪ Error occurred", "status_codes": [], "error": str(e)}

    status_codes = []
    try:
        for i in range(num_requests):
            response = requests.get(website, headers=headers)
            status_codes.append(response.status_code)
            if verbose:
                print(f"Request {i + 1}: Status Code {response.status_code}")
            time.sleep(delay)
        
        # Check for rate limiting (HTTP 429 Too Many Requests)
        if 429 in status_codes:
            if verbose:
                print(f"Rate limiting detected: Status codes: {status_codes}")
            return {"status": "🟢 Rate limiting detected", "status_codes": status_codes, "error": None}
        else:
            if verbose:
                print(f"No rate limiting detected: Status codes: {status_codes}")
            return {"status": "🔴 No rate limiting detected", "status_codes": status_codes, "error": None}

    except requests.exceptions.RequestException as e:
        if verbose:
            print(f"An error occurred while checking rate limiting for {website}: {e}")
        return {"status": "⚪ Error occurred", "status_codes": status_codes, "error": str(e)}
