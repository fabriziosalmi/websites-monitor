import requests

def check_cors_headers(website):
    try:
        response = requests.options(f"https://{website}")
        cors_header = response.headers.get('Access-Control-Allow-Origin', 'None')
        if cors_header != '*':
            return "🟢"
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking CORS headers for {website}: {e}")
        return "🔴"
