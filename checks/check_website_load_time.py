import time
import requests
from typing import Optional

def check_website_load_time(website: str) -> str:
    """
    Check the load time of the given website.
    
    Args:
    - website (str): The URL of the website to be checked.
    
    Returns:
    - str: "🟢" if load time is under 2 seconds,
           "🟠" if load time is between 2 and 4 seconds,
           "🔴" if load time is over 4 seconds,
           "⚪" in case of any errors or timeouts.
    """
    start_time = time.time()
    try:
        response = requests.get(f"https://{website}", timeout=10)
        elapsed_time = time.time() - start_time
        
        if elapsed_time < 2:
            return "🟢"
        elif elapsed_time < 4:
            return "🟠"
        else:
            return "🔴"
            
    except requests.Timeout:
        print(f"Timeout occurred while checking website load time for {website}.")
        return "⚪"
    except Exception as e:
        print(f"An error occurred while checking website load time for {website}: {e}")
        return "⚪"
