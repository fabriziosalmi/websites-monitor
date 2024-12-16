import requests
import time
import logging
from urllib.parse import urlparse, urlunparse

logger = logging.getLogger(__name__)

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

def check_rate_limiting(website, num_requests=5, delay=0.3, user_agent="RateLimitChecker/1.1", threshold=2):
    """
    Checks for rate limiting using a more accurate approach with varied delays.

    Args:
        website (str): The URL of the website to check.
        num_requests (int): Number of requests to send for testing.
        delay (float): Initial delay in seconds between requests.
        user_agent (str): Custom User-Agent string for the requests.
        threshold (int): The maximum number of successful requests before assuming no rate limiting.

    Returns:
        str: "🟢", "🔴", or "⚪" based on the detection status.
    """
    headers = {
        "User-Agent": user_agent
    }
    
     # Normalize the URL
    try:
        website = normalize_url(website)
    except Exception as e:
        logger.error(f"Invalid URL format: {e}")
        return "⚪"

    status_codes = []
    success_count = 0
    try:
        for i in range(num_requests):
          
            start_time = time.time()
            response = requests.get(website, headers=headers, timeout=10)
            end_time = time.time()
            status_codes.append(response.status_code)
            
            if response.status_code in [200, 201, 202, 203, 204, 205, 206]:
               success_count += 1
            elif response.status_code == 429:
                logger.info(f"Rate limiting detected for {website} after {i + 1} requests")
                return "🟢"
            
            elapsed_time = end_time - start_time
            time_to_sleep = max(0, delay - elapsed_time)
            time.sleep(time_to_sleep)
            

        if success_count >= threshold:
           logger.info(f"No rate limiting detected for {website}: Status codes: {status_codes}")
           return "🔴"
        else:
          logger.info(f"Rate limiting detected for {website}: Status codes: {status_codes}")
          return "🟢"

    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred while checking rate limiting for {website}: {e}")
        return "⚪"
    except Exception as e:
      logger.error(f"An unexpected error occurred while checking rate limiting for {website}: {e}")
      return "⚪"
