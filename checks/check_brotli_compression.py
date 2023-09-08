import requests

def check_brotli_compression(website):
    headers = {
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(f"https://{website}", headers=headers, timeout=10)
        
        if 'br' in response.headers.get('Content-Encoding', ''):
            return "🟢"
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking Brotli compression for {website}: {e}")
        return "⚪"
