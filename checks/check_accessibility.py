import requests

def check_accessibility(website):
    """
    Check the website's accessibility score using Lighthouse or similar services.
    
    Args:
    - website (str): URL of the website to be checked.
    
    Returns:
    - str: "🟢" if the accessibility score is high (0.9 to 1),
           "🟠" if the score is moderate (0.8 to 0.9),
           "🔴" if the score is low (less than 0.8),
           "⚪" for any errors.
    """
    LIGHTHOUSE_API_ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    
    params = {
        "url": website,
        "category": "accessibility"
    }

    try:
        response = requests.get(LIGHTHOUSE_API_ENDPOINT, params=params)
        data = response.json()
        score = data['lighthouseResult']['categories']['accessibility']['score']

        if score >= 0.9:
            return "🟢"  # Good accessibility score
        elif 0.8 <= score < 0.9:
            return "🟠"  # Moderate accessibility score
        else:
            return "🔴"  # Low accessibility score
    except Exception as e:
        print(f"Error checking accessibility for {website}. Error: {e}")
        return "⚪"  # Error occurred
