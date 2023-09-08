import requests
import time

def check_rate_limiting(website):
    """
    Check if a website implements rate limiting by sending multiple rapid requests.
    
    Args:
    - website (str): The URL of the website to check.
    
    Returns:
    - str: "🟢" if rate limiting is detected, "🔴" otherwise.
    """
    headers = {
        "User-Agent": "RateLimitChecker/1.0"
    }

    status_codes = []
    try:
        for _ in range(5):  # Sending 5 rapid requests
            response = requests.get(f"https://{website}", headers=headers)
            status_codes.append(response.status_code)
            time.sleep(0.5)  # Adding a half-second delay between requests

        # If any of the responses return a 429, we assume rate limiting is in place
        if 429 in status_codes:
            return "🟢"
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking rate limiting for {website}: {e}")
        return "🔴"
