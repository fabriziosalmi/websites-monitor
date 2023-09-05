import requests

def check_xss_protection(website):
    try:
        response = requests.get(f"https://{website}")
        if 'X-XSS-Protection' in response.headers:
            return "🟢"
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking XSS protection for {website}: {e}")
        return "🔴"
