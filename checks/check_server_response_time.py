import requests
import time
from requests.exceptions import RequestException, Timeout, HTTPError

def check_server_response_time(website: str) -> str:
    """
    Measure the server's response time.

    Args:
        website (str): URL of the website to be checked.

    Returns:
        str: 
            - "🟢" if the response time is excellent (under 0.5 seconds)
            - "🟠" if the response time is moderate (between 0.5 and 2 seconds)
            - "🔴" if the response time is slow (2 seconds or more)
            - "⚪" if an error occurs or the server does not respond in time
    """
    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        'User-Agent': 'ServerResponseTimeChecker/1.0'
    }

    try:
        # Start the timer
        start_time = time.time()

        # Make the request and measure the time taken
        response = requests.get(website, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # End the timer
        end_time = time.time()

        # Calculate the response time
        response_time = end_time - start_time

        # Determine the response time indicator
        if response_time < 0.5:
            print(f"Website {website} responded in {response_time:.2f} seconds (Excellent).")
            return "🟢"
        elif 0.5 <= response_time < 2:
            print(f"Website {website} responded in {response_time:.2f} seconds (Moderate).")
            return "🟠"
        else:
            print(f"Website {website} responded in {response_time:.2f} seconds (Slow).")
            return "🔴"

    except Timeout:
        print(f"Timeout occurred while checking server response time for {website}.")
        return "🔴"  # Red: Server did not respond in time.
    except HTTPError as e:
        print(f"HTTP error occurred while checking server response time for {website}: {e}")
        return "⚪"
    except RequestException as e:
        print(f"Request-related error occurred while checking server response time for {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking server response time for {website}: {e}")
        return "⚪"
