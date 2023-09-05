import ssl
import socket
from datetime import datetime

def check_ssl_cert(host, port=443):
    try:
        context = ssl.create_default_context()
        conn = socket.create_connection((host, port))
        sock = context.wrap_socket(conn, server_hostname=host)
        cert = sock.getpeercert()
        sock.close()

        cert_expiry = datetime.strptime(cert['notAfter'], r"%b %d %H:%M:%S %Y %Z")
        days_to_expire = (cert_expiry - datetime.utcnow()).days

        if days_to_expire <= 0:
            return "🔴"
        elif days_to_expire <= 30:
            return "🟠"
        else:
            return "🟢"
    except (ssl.SSLError, ssl.CertificateError):
        return "🔴"
