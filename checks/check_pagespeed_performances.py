import os
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
        api_key (str, optional): The Google PageSpeed Insights API key.
            Defaults to the PAGESPEED_API_KEY environment variable.

    Returns:
        str:
            - "🟢 (93/100, mobile)": the performance score with Lighthouse's
              bands, 🟢 90-100, 🟠 50-89, 🔴 0-49.
            - "⚪" if any errors occur during the check.
            - "⚪ (no PageSpeed API key)" if no API key is available.
    """
    # Input validation and URL normalization
    if not website or not isinstance(website, str):
        logger.error(f"Invalid website input: {website}")
        return "⚪"
        
    if not api_key:
        api_key = os.environ.get("PAGESPEED_API_KEY")
    if not api_key:
        logger.info("No PageSpeed API key (argument or PAGESPEED_API_KEY), skipping check.")
        return "⚪ (no PageSpeed API key)"
    
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
            score_percentage = round(score * 100)
            logger.info(f"PageSpeed score for {website} is {score_percentage}.")
            # Lighthouse's own bands: 90-100 good, 50-89 needs improvement,
            # 0-49 poor. A bare number carried no verdict for the UI or the
            # report to show.
            if score_percentage >= 90:
                verdict = "🟢"
            elif score_percentage >= 50:
                verdict = "🟠"
            else:
                verdict = "🔴"
            return f"{verdict} ({score_percentage}/100, mobile)"
            
        logger.warning(f"PageSpeed score not found for {website}.")
        return "⚪"

    # requests puts the full URL (with the API key) in its error messages:
    # never log the key.
    except Timeout:
        logger.error(f"Timeout occurred while fetching PageSpeed data for {website}")
        return "⚪"
    except HTTPError as http_err:
        logger.error(f"HTTP error occurred while fetching PageSpeed data for {website}: {str(http_err).replace(api_key, '***')}")
        return "⚪"
    except RequestException as req_err:
        logger.error(f"Request error occurred while fetching PageSpeed data for {website}: {str(req_err).replace(api_key, '***')}")
        return "⚪"
    except ValueError as json_err:
        logger.error(f"JSON parsing error occurred while fetching PageSpeed data for {website}: {json_err}")
        return "⚪"
    except Exception as e:
        logger.error(f"An unexpected error occurred while checking PageSpeed data for {website}: {e}")
        return "⚪"
