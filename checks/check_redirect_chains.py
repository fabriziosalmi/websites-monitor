import requests

def check_redirect_chains(website):
    try:
        response = requests.get(f"https://{website}", allow_redirects=False)
        if 'location' in response.headers:
            return "🔴"
        else:
            return "🟢"
    except Exception:
        return "🔴"
