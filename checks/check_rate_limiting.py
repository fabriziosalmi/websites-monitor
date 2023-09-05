import requests

def check_rate_limiting(website):
    try:
        for i in range(5):  # Sending 5 rapid requests
            response = requests.get(f"https://{website}")
        
        if response.status_code == 429:
            return "🟢"
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking rate limiting for {website}: {e}")
        return "🔴"
