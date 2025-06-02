import ssl
import socket
import logging
from datetime import datetime, timezone
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_ssl_cert(website: str, port: int = 443) -> str:
    """
    Check the SSL certificate of a given website for comprehensive security analysis.

    Args:
        website (str): The hostname or URL to check.
        port (int, optional): The port number. Defaults to 443 (standard HTTPS port).

    Returns:
        str:
            - "🟢 (X days left)" if the certificate is valid and secure with more than 30 days left.
            - "🟠 (X days left)" if the certificate is valid but has 30 days or fewer left, or minor issues.
            - "🔴" if the certificate is expired, invalid, or has security issues.
            - "⚪" if an error occurs during the check.
    """
    # Input validation and hostname extraction
    if not website or not isinstance(website, str):
        logger.error(f"Invalid website input: {website}")
        return "⚪"
    
    website = website.strip()
    
    # Extract hostname from URL if provided
    if website.startswith(('http://', 'https://')):
        parsed = urlparse(website)
        host = parsed.netloc.split(':')[0]
    else:
        host = website.split(':')[0]

    # Create enhanced SSL context
    context = ssl.create_default_context()
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED

    try:
        # Create connection with timeout
        with socket.create_connection((host, port), timeout=15) as conn:
            with context.wrap_socket(conn, server_hostname=host) as sock:
                cert = sock.getpeercert()
                cert_der = sock.getpeercert(binary_form=True)
                
                # Get protocol and cipher information
                protocol_version = sock.version()
                cipher_info = sock.cipher()

        # Extract certificate information
        subject = dict(x[0] for x in cert['subject'])
        issuer = dict(x[0] for x in cert['issuer'])
        
        # Parse certificate dates (handling timezone-aware parsing)
        not_before = datetime.strptime(cert['notBefore'], "%b %d %H:%M:%S %Y %Z")
        not_after = datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
        
        # Calculate days to expiration
        now = datetime.utcnow()
        days_to_expire = (not_after - now).days
        days_since_issued = (now - not_before).days

        # Security analysis
        security_issues = []
        
        # Check certificate validity period
        if days_to_expire <= 0:
            logger.error(f"SSL certificate for {host} is expired")
            return "🔴"
        
        # Check for short validity periods (potential security issue)
        cert_lifetime_days = (not_after - not_before).days
        if cert_lifetime_days > 825:  # More than ~2 years (old CA practice)
            security_issues.append("Long certificate lifetime")
        
        # Check signature algorithm
        if 'sha1' in cert.get('signatureAlgorithm', '').lower():
            security_issues.append("Weak signature algorithm (SHA-1)")
        
        # Check key size (for RSA certificates)
        public_key_info = cert.get('subjectPublicKeyInfo', {})
        
        # Check SAN (Subject Alternative Names)
        san_list = []
        for san in cert.get('subjectAltName', []):
            if san[0] == 'DNS':
                san_list.append(san[1])
        
        # Verify hostname is in certificate
        hostname_verified = (
            subject.get('commonName') == host or 
            host in san_list or
            any(san.replace('*.', '') in host for san in san_list if san.startswith('*.'))
        )
        
        if not hostname_verified:
            security_issues.append("Hostname not in certificate")

        # Check certificate chain and issuer
        if 'Let\'s Encrypt' in issuer.get('organizationName', ''):
            logger.debug(f"Let's Encrypt certificate for {host}")
        
        logger.info(f"SSL certificate analysis for {host}: {days_to_expire} days left, {len(security_issues)} issues")
        
        if security_issues:
            logger.warning(f"Security issues found: {security_issues}")

        # Determine result based on analysis
        if security_issues:
            if days_to_expire <= 7:
                return "🔴"
            elif days_to_expire <= 30:
                return f"🔴 ({days_to_expire} days left)"
            else:
                return f"🟠 ({days_to_expire} days left)"
        elif days_to_expire <= 7:
            return "🔴"
        elif days_to_expire <= 30:
            return f"🟠 ({days_to_expire} days left)"
        else:
            return f"🟢 ({days_to_expire} days left)"

    except ssl.SSLError as ssl_err:
        logger.error(f"SSL error for {host}:{port}: {ssl_err}")
        return "🔴"
    except socket.timeout:
        logger.warning(f"Connection timeout for {host}:{port}")
        return "⚪"
    except socket.error as sock_err:
        logger.warning(f"Socket error for {host}:{port}: {sock_err}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error for {host}:{port}: {e}")
        return "⚪"
