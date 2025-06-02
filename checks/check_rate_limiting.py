import requests
import time
import logging
from urllib.parse import urlparse, urlunparse
from requests.exceptions import RequestException, Timeout, HTTPError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def normalize_url(website):
    """
    Normalize the website URL, ensuring it has a scheme.
    
    Args:
    - website (str): The URL of the website to normalize.
    
    Returns:
    - str: The normalized URL.
    """
    if not website or not isinstance(website, str):
        raise ValueError("Invalid website input")
    
    website = website.strip()
    parsed_url = urlparse(website)
    
    if not parsed_url.scheme:
        normalized_url = urlunparse(('https', website, '', '', '', ''))
    else:
        normalized_url = website
    return normalized_url

def check_rate_limiting(website: str, num_requests: int = 5, delay: float = 0.3, 
                       user_agent: str = "RateLimitChecker/2.0", threshold: int = 2) -> str:
    """
    Checks for rate limiting using enhanced detection with varied delays and request patterns.

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
    response_times = []
    success_count = 0
    rate_limit_detected = False
    
    try:
        for i in range(num_requests):
            start_time = time.perf_counter()
            
            try:
                response = requests.get(website, headers=headers, timeout=15)
                end_time = time.perf_counter()
                
                response_time = end_time - start_time
                response_times.append(response_time)
                status_codes.append(response.status_code)
                
                # Check for rate limiting indicators
                if response.status_code == 429:
                    logger.info(f"Rate limiting detected (429) for {website} after {i + 1} requests")
                    rate_limit_detected = True
                    break
                elif response.status_code in [503, 502, 504]:
                    logger.warning(f"Server overload detected ({response.status_code}) for {website}")
                    # Continue to see if it's consistent
                    
                # Check for rate limiting headers
                rate_limit_headers = ['X-RateLimit-Limit', 'X-RateLimit-Remaining', 'Retry-After']
                if any(header in response.headers for header in rate_limit_headers):
                    logger.info(f"Rate limiting headers detected for {website}")
                    rate_limit_detected = True
                    break
                
                if response.status_code in [200, 201, 202, 203, 204, 205, 206]:
                    success_count += 1
                
                # Adaptive delay based on response time
                elapsed_time = end_time - start_time
                adaptive_delay = max(delay, elapsed_time * 0.5)
                time_to_sleep = max(0, adaptive_delay - elapsed_time)
                
                if i < num_requests - 1:
                    time.sleep(time_to_sleep)
                    
            except (Timeout, HTTPError) as e:
                logger.debug(f"Request {i + 1} failed for {website}: {e}")
                status_codes.append(0)  # Indicate failure
                time.sleep(delay * 2)  # Longer delay after failure

        # Enhanced analysis
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        logger.info(f"Rate limiting analysis for {website}: {success_count}/{num_requests} successful, "
                   f"avg response time: {avg_response_time:.3f}s")
        logger.debug(f"Status codes: {status_codes}")

        if rate_limit_detected:
            logger.info(f"Rate limiting detected for {website}")
            return "🟢"
        elif success_count < threshold:
            logger.info(f"Possible rate limiting detected for {website} (low success rate)")
            return "🟢"
        else:
            logger.info(f"No rate limiting detected for {website}")
            return "🔴"

    except RequestException as e:
        logger.error(f"Request error while checking rate limiting for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error while checking rate limiting for {website}: {e}")
        return "⚪"
