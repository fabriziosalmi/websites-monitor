import requests
from requests.exceptions import RequestException, HTTPError
import logging
logger = logging.getLogger(__name__)

def check_domain_breach(website: str) -> str:
    """
    Check if a domain has been found in any known data breaches.

    Args:
        website (str): The domain name to be checked.

    Returns:
        str:
            - "🟢" if no breaches are found.
            - "🔴" if the domain is found in any breaches.
            - "⚪" if any errors occurred or if the breach check could not be completed.
    """
    domain_breach = "🟢"  # Default to "safe" status.

    try:
        breach_url = f"https://breachdirectory.com/api/domain/{website}"
        response = requests.get(breach_url, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx).

        # Parse JSON response
        data = response.json()

        # Check if the domain was found in any breaches
        if data.get('found') is True:
           logger.info(f"Domain {website} has been found in a breach.")
           return "🔴"  # Red: Domain found in a breach.
        
        logger.info(f"Domain {website} has not been found in any breaches.")
        return domain_breach  # Green: No breaches found.

    except HTTPError as http_err:
        logger.error(f"HTTP error occurred while fetching breach data for {website}: {http_err}")
        return "⚪"  # Grey: API error.
    except RequestException as req_err:
        logger.error(f"Request error occurred while fetching breach data for {website}: {req_err}")
        return "⚪"  # Grey: Request error.
    except ValueError as json_err:
        logger.error(f"JSON parsing error occurred while fetching breach data for {website}: {json_err}")
        return "⚪"  # Grey: JSON parsing error.
    except Exception as e:
        logger.error(f"An unexpected error occurred while checking breach data for {website}: {e}")
        return "⚪"  # Grey: Unexpected error.
