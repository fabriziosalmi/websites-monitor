import ssl
import socket
from datetime import datetime

def check_ssl_cert(host, port=443):
    """
    Check the SSL certificate of a given host for its validity period.

    Args:
        host (str): The hostname to check.
        port (int, optional): The port number. Defaults to 443 (standard HTTPS port).

    Returns:
        str: 
            - "🟢" if the certificate is valid and has more than 30 days left.
            - "🟠" if the certificate is valid but has 30 days or fewer left.
            - "🔴" if the certificate is expired or there's an SSL related error.
    """
    context = ssl.create_default_context()

    try:
        with socket.create_connection((host, port)) as conn:
            with context.wrap_socket(conn, server_hostname=host) as sock:
                cert = sock.getpeercert()

        cert_expiry = datetime.strptime(cert['notAfter'], r"%b %d %H:%M:%S %Y %Z")
        days_to_expire = (cert_expiry - datetime.utcnow()).days

        if days_to_expire <= 0:
            return "🔴"
        elif days_to_expire <= 30:
            return "🟠"
        else:
            return "🟢"

    except (ssl.SSLError, ssl.CertificateError) as e:
        # In a real-world scenario, you might want to log the error for debugging.
        # print(f"SSL Error for {host} on port {port}: {e}")
        return "🔴"
    except Exception as e:
        # This block captures any other unexpected exceptions and provides an alert.
        print(f"Unexpected error while checking SSL certificate for {host} on port {port}: {e}")
        return "🔴"
