import socket
import ssl
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Updated cipher classifications based on current security standards
STRONG_CIPHERS = {
    'ECDHE-RSA-AES128-GCM-SHA256', 'ECDHE-RSA-AES256-GCM-SHA384',
    'ECDHE-ECDSA-AES128-GCM-SHA256', 'ECDHE-ECDSA-AES256-GCM-SHA384',
    'TLS_AES_128_GCM_SHA256', 'TLS_AES_256_GCM_SHA384',
    'TLS_CHACHA20_POLY1305_SHA256', 'ECDHE-RSA-CHACHA20-POLY1305',
    'ECDHE-ECDSA-CHACHA20-POLY1305'
}

MODERATE_CIPHERS = {
    'ECDHE-RSA-AES128-SHA', 'ECDHE-RSA-AES256-SHA',
    'ECDHE-ECDSA-AES128-SHA', 'ECDHE-ECDSA-AES256-SHA',
    'ECDHE-RSA-AES128-SHA256', 'ECDHE-RSA-AES256-SHA384'
}

WEAK_CIPHERS = {
    'RC4', 'DES', '3DES', 'MD5', 'SHA1', 'NULL'
}

def check_ssl_cipher_strength(website: str) -> str:
    """
    Check the strength of the SSL/TLS cipher suite of the website with enhanced analysis.

    Args:
        website (str): URL of the website to be checked.

    Returns:
        str:
            - "🟢" if the cipher strength is strong
            - "🟠" if the cipher strength is moderate
            - "🔴" if the cipher strength is weak
            - "⚪" for any errors
    """
    # Input validation and hostname extraction
    if not website or not isinstance(website, str):
        logger.error(f"Invalid website input: {website}")
        return "⚪"
    
    website = website.strip()
    
    # Extract hostname from URL
    if website.startswith(('http://', 'https://')):
        hostname = website.split('//')[1].split('/')[0].split(':')[0]
    else:
        hostname = website.split('/')[0].split(':')[0]

    try:
        # Create enhanced SSL context
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        
        # Create connection with timeout
        with socket.create_connection((hostname, 443), timeout=15) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                # Get comprehensive SSL information
                cipher_info = ssock.cipher()
                protocol_version = ssock.version()
                cert = ssock.getpeercert()

        if not cipher_info:
            logger.warning(f"No cipher information available for {hostname}")
            return "⚪"

        cipher_name = cipher_info[0]
        cipher_protocol = cipher_info[1] 
        cipher_bits = cipher_info[2]

        logger.info(f"SSL analysis for {hostname}: {cipher_name}, {protocol_version}, {cipher_bits} bits")

        # Enhanced cipher strength analysis
        cipher_upper = cipher_name.upper()
        
        # Check for weak indicators first
        if any(weak in cipher_upper for weak in WEAK_CIPHERS):
            logger.warning(f"Weak cipher components detected: {cipher_name}")
            return "🔴"
        
        # Check protocol version
        if protocol_version in ['TLSv1.3']:
            logger.info(f"Excellent protocol version: {protocol_version}")
            return "🟢"
        elif protocol_version in ['TLSv1.2']:
            # For TLS 1.2, check specific cipher
            if cipher_name in STRONG_CIPHERS:
                logger.info(f"Strong cipher with TLS 1.2: {cipher_name}")
                return "🟢"
            elif cipher_name in MODERATE_CIPHERS:
                logger.info(f"Moderate cipher with TLS 1.2: {cipher_name}")
                return "🟠"
            else:
                logger.warning(f"Unknown/weak cipher with TLS 1.2: {cipher_name}")
                return "🔴"
        elif protocol_version in ['TLSv1.1', 'TLSv1']:
            logger.warning(f"Outdated protocol version: {protocol_version}")
            return "🔴"
        else:
            logger.warning(f"Unknown protocol version: {protocol_version}")
            return "🔴"

    except socket.timeout:
        logger.warning(f"Connection timeout for {hostname}")
        return "⚪"
    except ssl.SSLError as ssl_err:
        logger.warning(f"SSL error for {hostname}: {ssl_err}")
        return "⚪"
    except socket.error as sock_err:
        logger.warning(f"Socket error for {hostname}: {sock_err}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error for {hostname}: {e}")
        return "⚪"
