import requests
import json

def check_pagespeed(website):
    # Your code to check PageSpeed
    pagespeed_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://{website}"
    pagespeed_response = requests.get(pagespeed_url)
    pagespeed_data = json.loads(pagespeed_response.text)
    pagespeed_score = pagespeed_data["lighthouseResult"]["categories"]["performance"]["score"] * 100
    return pagespeed_score
