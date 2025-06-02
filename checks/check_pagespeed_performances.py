import requests
import logging
from requests.exceptions import RequestException, HTTPError, Timeout

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_pagespeed_performances(website: str, api_key: str = None) -> str:
    """
    Checks the PageSpeed Insights performance score for a website with enhanced error handling.

    Args:
        website (str): The URL of the website to be checked.
        api_key (str, optional): The Google PageSpeed Insights API key. Defaults to None.

    Returns:
        str:
            - An integer representing the PageSpeed score if successful.
            - "⚪" if any errors occur during the check or if no API key was provided.
    """
    # Input validation and URL normalization
    if not website or not isinstance(website, str):
        logger.error(f"Invalid website input: {website}")
        return "⚪"
        
    if not api_key:
        logger.error("No API key provided for PageSpeed check.")
        return "⚪"
    
    website = website.strip()
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"
    
    try:
        # Enhanced API call with better parameters
        pagespeed_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        params = {
            'url': website,
            'key': api_key,
            'category': 'performance',
            'strategy': 'mobile'  # Default to mobile strategy
        }
        
        response = requests.get(pagespeed_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Enhanced data extraction
        lighthouse_result = data.get("lighthouseResult", {})
        performance_category = lighthouse_result.get("categories", {}).get("performance", {})
        score = performance_category.get("score")
        
        if score is not None:
            score_percentage = int(score * 100)
            logger.info(f"PageSpeed score for {website} is {score_percentage}.")
            return str(score_percentage)
            
        logger.warning(f"PageSpeed score not found for {website}.")
        return "⚪"

    except Timeout:
        logger.error(f"Timeout occurred while fetching PageSpeed data for {website}")
        return "⚪"
    except HTTPError as http_err:
        logger.error(f"HTTP error occurred while fetching PageSpeed data for {website}: {http_err}")
        return "⚪"
    except RequestException as req_err:
        logger.error(f"Request error occurred while fetching PageSpeed data for {website}: {req_err}")
        return "⚪"
    except ValueError as json_err:
        logger.error(f"JSON parsing error occurred while fetching PageSpeed data for {website}: {json_err}")
        return "⚪"
    except Exception as e:
        logger.error(f"An unexpected error occurred while checking PageSpeed data for {website}: {e}")
        return "⚪"
