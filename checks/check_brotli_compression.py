import requests
from requests.exceptions import RequestException, Timeout, HTTPError

def check_brotli_compression(website):
    """
    Check if the website supports Brotli compression.

    Args:
        website (str): The URL of the website to be checked.

    Returns:
        str: 
            - "🟢" if Brotli compression is enabled
            - "🔴" if Brotli compression is not enabled
            - "⚪" if an error occurs
    """
    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "BrotliCompressionChecker/1.0"
    }

    try:
        # Method 1: Direct HTTP Request with Brotli Accept-Encoding Header
        response = requests.get(website, headers=headers, timeout=10)
        response.raise_for_status()

        # Check if the response indicates Brotli compression
        if 'br' in response.headers.get('Content-Encoding', ''):
            print(f"Brotli compression is enabled for {website}.")
            return "🟢"
        else:
            print(f"Brotli compression is not enabled for {website}.")
            return "🔴"

    except (Timeout, HTTPError, RequestException) as e:
        print(f"Request error occurred while checking Brotli compression for {website}: {e}")
        
        # Method 2: Alternative Check via Content-Length Comparison (Fallback)
        try:
            headers_gzip = {
                "Accept-Encoding": "gzip, deflate",
                "User-Agent": "BrotliCompressionChecker/1.0"
            }
            headers_brotli = {
                "Accept-Encoding": "br",
                "User-Agent": "BrotliCompressionChecker/1.0"
            }

            # Request with Gzip/Deflate encoding
            response_gzip = requests.get(website, headers=headers_gzip, timeout=10)
            response_gzip.raise_for_status()
            
            # Request with Brotli encoding
            response_brotli = requests.get(website, headers=headers_brotli, timeout=10)
            response_brotli.raise_for_status()

            # Check if Brotli encoding is actually used in response
            if 'br' in response_brotli.headers.get('Content-Encoding', ''):
                print(f"Brotli compression is enabled for {website} (fallback method).")
                return "🟢"
            else:
                print(f"Brotli compression is not enabled for {website} (fallback method).")
                return "🔴"

        except Exception as e:
            print(f"Error during fallback Brotli check for {website}: {e}")
            return "⚪"

    return "⚪"
