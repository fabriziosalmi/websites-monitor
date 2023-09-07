import requests

def check_ssl_cipher_strength(website):
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
        response = requests.get(f"https://{website}")
        cipher = response.raw.connection.socket.get_cipher()[0]

        # Depending on your security requirements, adjust these
        strong_ciphers = ['ECDHE-RSA-AES128-GCM-SHA256', 'ECDHE-RSA-AES256-GCM-SHA384']
        moderate_ciphers = ['ECDHE-RSA-AES128-SHA', 'ECDHE-RSA-AES256-SHA']
        
        if cipher in strong_ciphers:
            return "🟢"
        elif cipher in moderate_ciphers:
            return "🟠"
        else:
            return "🔴"

    except Exception as e:
        print(f"Error occurred: {e}")
        return "⚪"

print(check_ssl_cipher_strength("https://example.com"))
