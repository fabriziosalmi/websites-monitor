import requests

def check_hsts(website):
    """
    Check if the website implements HTTP Strict Transport Security (HSTS).
    
    Args:
    - website (str): URL of the website to be checked.
    
    Returns:
    - str: "🟢" if the site has HSTS enabled, "🔴" otherwise.
    """
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
    }
    
    try:
        response = requests.get(f"https://{website}", headers=headers, timeout=10)
        
        if 'Strict-Transport-Security' in response.headers:
            return "🟢"
        else:
            return "🔴"
    except requests.RequestException as e:
        print(f"An error occurred while checking HSTS for {website}: {e}")
        return "🔴"
