import requests

def check_ad_and_tracking(website):
    try:
        response = requests.get(f"https://{website}")
        if "google-analytics" in response.text and "adsbygoogle" in response.text:
            return "🔴"
        elif "google-analytics" in response.text:
            return "🟠"
        else:
            return "🟢"
    except Exception as e:
        print(f"An error occurred while checking for ad network and tracking scripts for {website}: {e}")
        return "🔴"
