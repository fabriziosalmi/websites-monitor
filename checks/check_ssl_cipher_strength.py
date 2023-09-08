import requests

STRONG_CIPHERS = {'ECDHE-RSA-AES128-GCM-SHA256', 'ECDHE-RSA-AES256-GCM-SHA384'}
MODERATE_CIPHERS = {'ECDHE-RSA-AES128-SHA', 'ECDHE-RSA-AES256-SHA'}

def check_ssl_cipher_strength(website: str) -> str:
    """
    Check the strength of the SSL/TLS cipher suite of the website.
    
    Args:
    - website (str): URL of the website to be checked.
    
    Returns:
    - str: "🟢" if the cipher strength is strong,
           "🟠" if the cipher strength is moderate,
           "🔴" if the cipher strength is weak,
           "⚪" for any errors.
    """
    try:
        with requests.Session() as session:
            response = session.get(f"https://{website}")
            cipher = response.raw.connection.socket.get_cipher()[0]
        
        if cipher in STRONG_CIPHERS:
            return "🟢"
        elif cipher in MODERATE_CIPHERS:
            return "🟠"
        else:
            return "🔴"
    except requests.RequestException as req_err:
        print(f"Request error: {req_err}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return "⚪"
