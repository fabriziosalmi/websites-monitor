import requests

def check_redirects(website):
    try:
        response = requests.get(f"http://{website}", allow_redirects=False)
        if response.status_code in [301, 302] and 'https' in response.headers.get('Location', ''):
            return "🟢"
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking redirects for {website}: {e}")
        return "🔴"
