import requests
import json
from requests.exceptions import RequestException, Timeout, HTTPError

def check_pagespeed_performances(website: str, api_key: str) -> int:
    """
    Check the PageSpeed performance score of the given website using Google's PageSpeed Insights API.

    Args:
        website (str): The URL of the website to be checked.
        api_key (str): The API key for accessing the PageSpeed Insights API.

    Returns:
        int: The PageSpeed performance score (0-100), or 0 in case of any errors.
    """
    # Construct the PageSpeed API URL
    pagespeed_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://{website}&key={api_key}"
    
    headers = {
        'User-Agent': 'PageSpeedChecker/1.0'
    }

    try:
        # Make a request to the PageSpeed Insights API
        pagespeed_response = requests.get(pagespeed_url, headers=headers, timeout=10)
        pagespeed_response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the API response JSON
        pagespeed_data = pagespeed_response.json()

        # Extract the performance score
        pagespeed_score = pagespeed_data["lighthouseResult"]["categories"]["performance"]["score"] * 100

        # Return the rounded score as an integer
        print(f"PageSpeed score for {website} is {round(pagespeed_score)}.")
        return round(pagespeed_score)

    except (Timeout, HTTPError) as e:
        print(f"Timeout or HTTP error occurred while fetching PageSpeed data for {website}: {e}")
        return 0
    except RequestException as e:
        print(f"Request-related error occurred while fetching PageSpeed data for {website}: {e}")
        return 0
    except KeyError:
        print(f"Error parsing PageSpeed data for {website}: The expected data structure was not found.")
        return 0
    except Exception as e:
        print(f"An unexpected error occurred while checking PageSpeed for {website}: {e}")
        return 0
