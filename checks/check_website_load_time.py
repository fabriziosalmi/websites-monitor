import time
import statistics
import requests
import logging
from requests.exceptions import RequestException, Timeout, HTTPError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_website_load_time(website: str, num_attempts: int = 3) -> str:
    """
    Check the load time of the given website with multiple measurements for accuracy.
    
    Args:
        website (str): The URL of the website to be checked.
        num_attempts (int): Number of attempts to measure load time for accuracy.
    
    Returns:
        str: 
            - "🟢" if average load time is under 2 seconds
            - "🟠" if average load time is between 2 and 4 seconds
            - "🔴" if average load time is over 4 seconds
            - "⚪" in case of any errors or timeouts
    """
    # Input validation and URL normalization
    if not website or not isinstance(website, str):
        logger.error(f"Invalid website input: {website}")
        return "⚪"
    
    website = website.strip()
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }

    load_times = []
    
    try:
        # Perform multiple measurements for accuracy
        for attempt in range(num_attempts):
            start_time = time.perf_counter()
            
            # Perform the request with enhanced monitoring
            response = requests.get(
                website, 
                headers=headers, 
                timeout=15,
                allow_redirects=True,
                stream=False
            )
            response.raise_for_status()
            
            # Calculate elapsed time
            elapsed_time = time.perf_counter() - start_time
            load_times.append(elapsed_time)
            
            logger.debug(f"Attempt {attempt + 1} for {website}: {elapsed_time:.3f}s")
            
            # Small delay between attempts to avoid overwhelming the server
            if attempt < num_attempts - 1:
                time.sleep(0.5)

        # Calculate statistics
        avg_time = statistics.mean(load_times)
        median_time = statistics.median(load_times)
        min_time = min(load_times)
        max_time = max(load_times)
        
        logger.info(f"Load time stats for {website} - Avg: {avg_time:.3f}s, Median: {median_time:.3f}s, Range: {min_time:.3f}s-{max_time:.3f}s")

        # Enhanced categorization based on average time
        if avg_time < 1.0:
            logger.info(f"Website {website} loaded very fast: {avg_time:.2f}s average")
            return "🟢"
        elif avg_time < 2.0:
            logger.info(f"Website {website} loaded fast: {avg_time:.2f}s average")
            return "🟢"
        elif avg_time < 4.0:
            logger.info(f"Website {website} loaded moderately: {avg_time:.2f}s average")
            return "🟠"
        else:
            logger.warning(f"Website {website} loaded slowly: {avg_time:.2f}s average")
            return "🔴"

    except Timeout:
        logger.warning(f"Timeout occurred while checking load time for {website}")
        return "🔴"  # Timeout is effectively a slow load time
    except HTTPError as e:
        logger.warning(f"HTTP error for {website}: {e}")
        return "⚪"
    except RequestException as e:
        logger.warning(f"Request error for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error for {website}: {e}")
        return "⚪"
