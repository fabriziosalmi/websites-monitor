import requests

def check_ad_and_tracking(website):
    """
    Check if the website is using Google Analytics and/or AdsbyGoogle.

    Returns:
        "🔴" if both are present
        "🟠" if only Google Analytics is present
        "🟢" if neither are present
    """

    try:
        response = requests.get(f"https://{website}", timeout=10)  # Adding a timeout of 10 seconds

        # Determine the status based on the presence of the scripts
        has_google_analytics = "google-analytics" in response.text
        has_adsbygoogle = "adsbygoogle" in response.text

        if has_google_analytics and has_adsbygoogle:
            return "🔴"
        elif has_google_analytics:
            return "🟠"
        else:
            return "🟢"
    except Exception as e:
        print(f"An error occurred while checking for ad network and tracking scripts for {website}: {e}")
        return "⚪"
