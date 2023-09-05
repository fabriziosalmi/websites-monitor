import requests

def check_favicon(website):
    try:
        response = requests.get(f"https://{website}/favicon.ico")
        if response.status_code == 200:
            return "🟢"
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking favicon for {website}: {e}")
        return "🔴"
