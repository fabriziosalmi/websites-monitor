import re
import requests

def check_privacy_exposure(website):
    try:
        response = requests.get(f"https://{website}")
        sensitive_data_patterns = [r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', r'\d{10}']
        for pattern in sensitive_data_patterns:
            if re.search(pattern, response.text):
                return "🔴"
        return "🟢"
    except Exception as e:
        print(f"An error occurred while checking for privacy exposure for {website}: {e}")
        return "🔴"
