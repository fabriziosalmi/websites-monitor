import requests

def check_hsts(website):
    try:
        response = requests.get(f"https://{website}")
        if 'Strict-Transport-Security' in response.headers:
            return "🟢"
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking HSTS for {website}: {e}")
        return "🔴"
