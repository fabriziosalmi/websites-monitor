import requests
import logging
from requests.exceptions import RequestException, Timeout, HTTPError

logger = logging.getLogger(__name__)

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
        "User-Agent": "RobotsTxtChecker/1.1"
    }

    try:
        # Perform the HTTP request with a timeout
        response = requests.get(f"{website}/robots.txt", headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Check for presence of specific directives in the robots.txt content
        content = response.text.lower()
        if "user-agent" in content or "disallow" in content:
            logger.info(f"Valid robots.txt found for {website}.")
            return "🟢"
        logger.warning(f"Invalid robots.txt found for {website}.")
        return "🔴"
    
    except (Timeout, HTTPError) as e:
        logger.warning(f"Timeout or HTTP error occurred while checking robots.txt for {website}: {e}")
        return "⚪"
    except RequestException as e:
        logger.error(f"An error occurred while checking robots.txt for {website}: {e}")
        return "⚪"
    except Exception as e:
       logger.error(f"An unexpected error occurred while checking robots.txt for {website}: {e}")
       return "⚪"
