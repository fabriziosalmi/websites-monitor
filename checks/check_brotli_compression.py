import requests

def check_brotli_compression(website):
    response = requests.get(f"https://{website}")
    if 'br' in response.headers.get('Content-Encoding', ''):
        return "🟢"
    else:
        return "🔴"
