import ssl
import socket
from datetime import datetime

def check_ssl_cert(host: str, port: int = 443) -> str:
    """
    Check the SSL certificate of a given host for its validity period.

    Args:
        host (str): The hostname to check.
        port (int, optional): The port number. Defaults to 443 (standard HTTPS port).

    Returns:
        str:
            - "🟢 (X days left)" if the certificate is valid and has more than 30 days left.
            - "🟠 (X days left)" if the certificate is valid but has 30 days or fewer left.
            - "🔴" if the certificate is expired or there's an SSL-related error.
            where X is the number of days left for the SSL certificate to expire.
    """
    context = ssl.create_default_context()

    try:
        # Create a connection to the host and retrieve the SSL certificate
        with socket.create_connection((host, port), timeout=10) as conn:
            with context.wrap_socket(conn, server_hostname=host) as sock:
                cert = sock.getpeercert()

        # Extract the certificate expiration date
        cert_expiry = datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
        days_to_expire = (cert_expiry - datetime.utcnow()).days

        # Determine the result based on the number of days left until expiration
        if days_to_expire <= 0:
            print(f"SSL certificate for {host} is expired.")
            return "🔴"
        elif days_to_expire <= 30:
            print(f"SSL certificate for {host} is valid but has {days_to_expire} days left.")
            return f"🟠 ({days_to_expire} days left)"
        else:
            print(f"SSL certificate for {host} is valid with {days_to_expire} days left.")
            return f"🟢 ({days_to_expire} days left)"

    except (ssl.SSLError, ssl.CertificateError) as ssl_err:
        print(f"SSL error for {host} on port {port}: {ssl_err}")
        return "🔴"
    except socket.timeout:
        print(f"Connection to {host} on port {port} timed out.")
        return "🔴"
    except socket.error as sock_err:
        print(f"Socket error for {host} on port {port}: {sock_err}")
        return "🔴"
    except Exception as e:
        print(f"Unexpected error while checking SSL certificate for {host} on port {port}: {e}")
        return "🔴"
