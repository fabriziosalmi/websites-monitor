import requests
import json

def check_pagespeed(website):
    try:
        pagespeed_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://{website}"
        pagespeed_response = requests.get(pagespeed_url)
        pagespeed_data = json.loads(pagespeed_response.text)

        # Get the PageSpeed score and convert it to a percentage
        pagespeed_score = pagespeed_data["lighthouseResult"]["categories"]["performance"]["score"] * 100

        # Return the score as a green/yellow/red indicator
        if pagespeed_score >= 90:
            return f"🟢 {pagespeed_score}"
        elif pagespeed_score >= 50:
            return f"🟠 {pagespeed_score}"
        else:
            return f"🔴 {pagespeed_score}"
    except Exception as e:
        print(f"An error occurred while checking PageSpeed for {website}: {e}")
        return "🔴 Error"
