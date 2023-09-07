import requests
import json

def check_pagespeed_pwa(website):
    try:
        pagespeed_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://{website}"
        pagespeed_response = requests.get(pagespeed_url)
        
        # Check if the API responded with a valid response
        if pagespeed_response.status_code != 200:
            print(f"Error occurred while fetching PageSpeed for {website}. Status Code: {pagespeed_response.status_code}")
            return 0  # Returning 0 as an indication of an API error
        
        pagespeed_data = json.loads(pagespeed_response.text)
        pagespeed_score = pagespeed_data["lighthouseResult"]["categories"]["pwa"]["score"] * 100

        # Rounding the score to ensure it's an integer
        return round(pagespeed_score)
        
    except Exception as e:
        print(f"An error occurred while checking PageSpeed for {website}: {e}")
        return 0  # Returning 0 as an indication of a processing error
