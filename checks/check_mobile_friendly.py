import requests
import json

def check_mobile_friendly(website, api_key):
    try:
        api_url = f"https://searchconsole.googleapis.com/v1/urlTestingTools/mobileFriendlyTest:run?key={api_key}"
        payload = json.dumps({"url": f"https://{website}"})
        headers = {'Content-Type': 'application/json'}
        response = requests.post(api_url, headers=headers, data=payload)
        result = json.loads(response.text)

        if result.get('mobileFriendliness') == 'MOBILE_FRIENDLY':
            return "🟢"
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking mobile-friendliness for {website}: {e}")
        return "🔴"
