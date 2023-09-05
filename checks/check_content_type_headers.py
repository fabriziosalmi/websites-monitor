import requests

def check_content_type_headers(website):
    try:
        response = requests.get(f"https://{website}")
        content_type = response.headers.get('Content-Type')
        
        if 'text/html' in content_type:
            return "🟢"
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking Content-Type headers for {website}: {e}")
        return "🔴"
