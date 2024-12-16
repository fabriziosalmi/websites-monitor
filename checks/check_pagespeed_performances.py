import requests
import logging
from requests.exceptions import RequestException, HTTPError

logger = logging.getLogger(__name__)

def check_pagespeed_performances(website: str, api_key: str = None) -> str:
    """
    Checks the PageSpeed Insights performance score for a website.

    Args:
        website (str): The URL of the website to be checked.
        api_key (str, optional): The Google PageSpeed Insights API key. Defaults to None.

    Returns:
        str:
            - An integer representing the PageSpeed score if successful.
            - "⚪" if any errors occur during the check or if no API key was provided.
    """
    if not api_key:
      logger.error("No API key provided for PageSpeed check.")
      return "⚪"
    
    try:
        pagespeed_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={website}&key={api_key}"
        response = requests.get(pagespeed_url, timeout=20)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx).
        data = response.json()

        score = data.get("lighthouseResult", {}).get("categories", {}).get("performance", {}).get("score")
        if score is not None:
            logger.info(f"PageSpeed score for {website} is {int(score * 100)}.")
            return str(int(score * 100))
        logger.warning(f"PageSpeed score not found for {website}.")
        return "⚪"

    except HTTPError as http_err:
        logger.error(f"Timeout or HTTP error occurred while fetching PageSpeed data for {website}: {http_err}")
        return "⚪"  # Grey: API error.
    except RequestException as req_err:
        logger.error(f"Timeout or HTTP error occurred while fetching PageSpeed data for {website}: {req_err}")
        return "⚪"  # Grey: Request error.
    except ValueError as json_err:
        logger.error(f"JSON parsing error occurred while fetching PageSpeed data for {website}: {json_err}")
        return "⚪"  # Grey: JSON parsing error.
    except Exception as e:
        logger.error(f"An unexpected error occurred while checking PageSpeed data for {website}: {e}")
        return "⚪"  # Grey: Unexpected error.
