import requests
from requests.exceptions import RequestException, Timeout, HTTPError

def check_robot_txt(website):
    """
    Verify the presence and basic validity of a robots.txt file on a website.
    
    Args:
    - website (str): The URL (without protocol) of the website to check.
    
    Returns:
    - str: "🟢" if the site has a valid robots.txt file, "🔴" otherwise, and 
           "⚪" in case of an error.
    """
    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        "User-Agent": "RobotsTxtChecker/1.0"
    }

    try:
        # Perform the HTTP request with a timeout
        response = requests.get(f"{website}/robots.txt", headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Check for presence of specific directives in the robots.txt content
        content = response.text.lower()
        if "user-agent" in content or "disallow" in content:
            return "🟢"
        return "🔴"
    
    except (Timeout, HTTPError) as e:
        print(f"Timeout or HTTP error occurred while checking robots.txt for {website}: {e}")
    except RequestException as e:
        print(f"An error occurred while checking robots.txt for {website}: {e}")
    
    return "⚪"
