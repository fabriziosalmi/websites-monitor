import requests
import time

def check_server_response_time(website):
    """
    Measure the server's response time.

    Args:
    - website (str): URL of the website to be checked.

    Returns:
    - str: Server response time indicator.
    """
    try:
        start_time = time.time()
        response = requests.get(website, timeout=10)
        end_time = time.time()

        response_time = end_time - start_time

        if response_time < 0.5:
            return "🟢"  # Green: Excellent response time.
        elif 0.5 <= response_time < 2:
            return "🟠"  # Orange: Moderate response time.
        else:
            return "🔴"  # Red: Slow response time.
    except requests.Timeout:
        return "🔴"  # Red: Server did not respond in time.
    except Exception as e:
        print(f"Error encountered: {e}")
        return "⚪"  # Grey: An error occurred while checking.
