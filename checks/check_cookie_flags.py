import requests

def check_cookie_flags(website):
    try:
        response = requests.get(f"https://{website}")
        cookie_flags = response.headers.get('Set-Cookie', '')
        if 'Secure' in cookie_flags and 'HttpOnly' in cookie_flags:
            return "🟢"
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking cookie flags for {website}: {e}")
        return "🔴"
