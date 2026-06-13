import whois
import logging
from whois.parser import PywhoisError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _normalize_field_value(value):
    """
    Normalize a WHOIS field value to a lowercase string for privacy checking.
    Handles strings, lists, dicts, and None values robustly.
    """
    if value is None:
        return ''
    if isinstance(value, str):
        return value.lower()
    if isinstance(value, list):
        return ' '.join(str(v).lower() for v in value if v is not None)
    if isinstance(value, dict):
        return ' '.join(f"{k} {v}" for k, v in value.items() if v is not None)
    return str(value).lower()

def check_privacy_protected_whois(domain: str) -> str:
    """
    Check if a domain's WHOIS information indicates that it is privacy-protected with enhanced detection.

    Args:
        domain (str): The domain to check.

    Returns:
        str: "🟢" if the domain's WHOIS information is privacy-protected, "🔴" otherwise,
             "⚪" if an error occurred.
    """
    # Input validation
    if not domain or not isinstance(domain, str):
        logger.error(f"Invalid domain input: {domain}")
        return "⚪"
    
    domain = domain.strip()
    
    # Remove protocol if present
    if domain.startswith(('http://', 'https://')):
        from urllib.parse import urlparse
        parsed = urlparse(domain)
        domain = parsed.netloc

    try:
        # Fetch WHOIS data for the domain
        whois_data = whois.whois(domain)

        # Enhanced privacy indicators
        privacy_indicators = [
            'privacy', 'protected', 'redacted', 'whoisguard', 'domains by proxy',
            'anonymous', 'contact privacy', 'whois privacy', 'perfect privacy', 
            'data protected', 'private registration', 'domain privacy',
            'namecheap', 'godaddy privacy', 'cloudflare', 'proxy protection',
            'withheld', 'not disclosed', 'see privacy policy'
        ]

        # Enhanced fields to check with more comprehensive coverage
        fields_to_check = [
            'registrar', 'tech_email', 'admin_email', 'registrant_email',
            'org', 'name', 'address', 'registrant_name', 'admin_name', 'tech_name',
            'registrant_org', 'admin_org', 'tech_org', 'emails'
        ]

        privacy_score = 0
        total_checks = 0

        # Check for privacy indicators in relevant WHOIS fields
        for field in fields_to_check:
            field_value = whois_data.get(field, '')
            
            if field_value:
                total_checks += 1
                field_str = _normalize_field_value(field_value)
                
                if any(indicator in field_str for indicator in privacy_indicators):
                    privacy_score += 1
                    logger.debug(f"Privacy indicator found in {field}: {field_value}")

        # Additional checks for redacted information
        if whois_data:
            # Check if critical information is redacted
            critical_fields = ['registrant_name', 'admin_email', 'tech_email']
            redacted_count = 0
            
            for field in critical_fields:
                value = whois_data.get(field, '')
                normalized = _normalize_field_value(value)
                if not normalized or 'redacted' in normalized or 'withheld' in normalized:
                    redacted_count += 1

            if redacted_count >= 2:
                privacy_score += 2

        logger.info(f"Privacy analysis for {domain}: score {privacy_score}/{total_checks + 2}")

        # Determine result based on privacy score
        if privacy_score > 0:
            logger.info(f"Privacy protection detected for {domain}")
            return "🟢"
        else:
            logger.warning(f"No privacy protection detected for {domain}")
            return "🔴"

    except PywhoisError as e:
        logger.warning(f"WHOIS command failed for {domain}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error while checking privacy-protected WHOIS for {domain}: {e}")
        return "⚪"
