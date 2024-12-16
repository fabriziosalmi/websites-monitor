import requests
import logging
from requests.exceptions import RequestException, HTTPError
import json

logger = logging.getLogger(__name__)

def check_domain_breach(website: str) -> str:
    """
    Check if a domain has been found in any known data breaches using the Have I Been Pwned API.

    Args:
        website (str): The domain name to be checked.

    Returns:
        str:
            - "🟢" if no breaches are found.
            - "🔴" if the domain is found in any breaches.
            - "⚪" if any errors occurred or if the breach check could not be completed.
    """
    try:
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{website}"
        response = requests.get(url, headers={"hibp-api-version": "3"}, timeout=10)
        response.raise_for_status()
        if response.status_code == 200:
            breaches = response.json()
            if breaches:
                logger.warning(f"Domain {website} has been found in a breach.")
                return "🔴"
            logger.info(f"Domain {website} has not been found in any breaches.")
            return "🟢"
    except requests.exceptions.RequestException as e:
        if e.response is not None and e.response.status_code == 401:
            logger.error(f"Request error occurred while fetching breach data for {website}: {e}")
            return "⚪"
        else:
            logger.error(f"Request error occurred while fetching breach data for {website}: {e}")
            return "⚪"
    except json.JSONDecodeError as e:
      logger.error(f"Request error occurred while fetching breach data for {website}: {e}")
      return "⚪"
    except Exception as e:
        logger.error(f"An unexpected error occurred while checking breach data for {website}: {e}")
        return "⚪"
