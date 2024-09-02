import socket
import ssl

STRONG_CIPHERS = {'ECDHE-RSA-AES128-GCM-SHA256', 'ECDHE-RSA-AES256-GCM-SHA384'}
MODERATE_CIPHERS = {'ECDHE-RSA-AES128-SHA', 'ECDHE-RSA-AES256-SHA'}

def check_ssl_cipher_strength(website: str) -> str:
    """
    Check the strength of the SSL/TLS cipher suite of the website.

    Args:
        website (str): URL of the website to be checked.

    Returns:
        str:
            - "🟢" if the cipher strength is strong
            - "🟠" if the cipher strength is moderate
            - "🔴" if the cipher strength is weak
            - "⚪" for any errors
    """
    # Extract the hostname from the URL
    if website.startswith(('http://', 'https://')):
        hostname = website.split('//')[1]
    else:
        hostname = website

    try:
        # Create a socket and wrap it with SSL
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cipher = ssock.cipher()[0]  # Get the cipher suite name

        # Determine the strength of the cipher suite
        if cipher in STRONG_CIPHERS:
            print(f"Strong cipher used: {cipher} for {website}.")
            return "🟢"
        elif cipher in MODERATE_CIPHERS:
            print(f"Moderate cipher used: {cipher} for {website}.")
            return "🟠"
        else:
            print(f"Weak or unknown cipher used: {cipher} for {website}.")
            return "🔴"

    except (socket.timeout, ssl.SSLError) as ssl_err:
        print(f"SSL error occurred while checking cipher strength for {website}: {ssl_err}")
        return "⚪"
    except socket.error as sock_err:
        print(f"Socket error occurred while checking cipher strength for {website}: {sock_err}")
        return "⚪"
    except Exception as e:
        print(f"Unexpected error occurred while checking cipher strength for {website}: {e}")
        return "⚪"
