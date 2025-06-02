import requests
import time
import statistics
import logging
from requests.exceptions import RequestException, Timeout, HTTPError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_server_response_time(website: str, num_attempts: int = 3) -> str:
    """
    Measure the server's response time with multiple attempts for accuracy.

    Args:
        website (str): URL of the website to be checked.
        num_attempts (int): Number of attempts to measure response time.

    Returns:
        str: 
            - "🟢" if the response time is excellent (under 0.5 seconds)
            - "🟠" if the response time is moderate (between 0.5 and 2 seconds)
            - "🔴" if the response time is slow (2 seconds or more)
            - "⚪" if an error occurs or the server does not respond in time
    """
    # Input validation and URL normalization
    if not website or not isinstance(website, str):
        logger.error(f"Invalid website input: {website}")
        return "⚪"
    
    website = website.strip()
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response_times = []

    try:
        # Perform multiple measurements for accuracy
        for attempt in range(num_attempts):
            start_time = time.perf_counter()

            # Make the request and measure time to first byte
            response = requests.get(website, headers=headers, timeout=15, stream=True)
            
            # Time to first byte
            ttfb = time.perf_counter() - start_time
            response.raise_for_status()
            
            response_times.append(ttfb)
            logger.debug(f"Attempt {attempt + 1} for {website}: {ttfb:.3f}s")
            
            # Small delay between attempts
            if attempt < num_attempts - 1:
                time.sleep(0.5)

        # Calculate statistics
        avg_time = statistics.mean(response_times)
        median_time = statistics.median(response_times)
        min_time = min(response_times)
        max_time = max(response_times)

        logger.info(f"Response time stats for {website} - Avg: {avg_time:.3f}s, Median: {median_time:.3f}s, Range: {min_time:.3f}s-{max_time:.3f}s")

        # Enhanced categorization based on average response time
        if avg_time < 0.2:
            logger.info(f"Website {website} responded excellently: {avg_time:.3f}s average")
            return "🟢"
        elif avg_time < 0.5:
            logger.info(f"Website {website} responded very well: {avg_time:.3f}s average")
            return "🟢"
        elif avg_time < 2.0:
            logger.info(f"Website {website} responded moderately: {avg_time:.3f}s average")
            return "🟠"
        else:
            logger.warning(f"Website {website} responded slowly: {avg_time:.3f}s average")
            return "🔴"

    except Timeout:
        logger.warning(f"Timeout occurred while checking response time for {website}")
        return "🔴"
    except HTTPError as e:
        logger.warning(f"HTTP error for {website}: {e}")
        return "⚪"
    except RequestException as e:
        logger.warning(f"Request error for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error for {website}: {e}")
        return "⚪"
