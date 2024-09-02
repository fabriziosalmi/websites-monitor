import time
import requests
from requests.exceptions import RequestException, Timeout, HTTPError

def check_website_load_time(website: str) -> str:
    """
    Check the load time of the given website.
    
    Args:
        website (str): The URL of the website to be checked.
    
    Returns:
        str: 
            - "🟢" if load time is under 2 seconds
            - "🟠" if load time is between 2 and 4 seconds
            - "🔴" if load time is over 4 seconds
            - "⚪" in case of any errors or timeouts
    """
    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        'User-Agent': 'WebsiteLoadTimeChecker/1.0'
    }

    try:
        # Start the timer
        start_time = time.time()

        # Perform the request
        response = requests.get(website, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Calculate the elapsed time
        elapsed_time = time.time() - start_time

        # Determine the result based on the load time
        if elapsed_time < 2:
            print(f"Website {website} loaded in {elapsed_time:.2f} seconds (Fast).")
            return "🟢"
        elif elapsed_time < 4:
            print(f"Website {website} loaded in {elapsed_time:.2f} seconds (Moderate).")
            return "🟠"
        else:
            print(f"Website {website} loaded in {elapsed_time:.2f} seconds (Slow).")
            return "🔴"

    except Timeout:
        print(f"Timeout occurred while checking website load time for {website}.")
        return "⚪"
    except HTTPError as e:
        print(f"HTTP error occurred while checking website load time for {website}: {e}")
        return "⚪"
    except RequestException as e:
        print(f"Request-related error occurred while checking website load time for {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking website load time for {website}: {e}")
        return "⚪"
