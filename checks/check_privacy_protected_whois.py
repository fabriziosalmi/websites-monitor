import whois
from whois.exceptions import WhoisCommandFailed

def check_privacy_protected_whois(domain):
    """
    Check if a domain's WHOIS information indicates that it is privacy-protected.
    
    Args:
    - domain (str): The domain to check.
    
    Returns:
    - str: "🟢" if the domain's WHOIS information is privacy-protected, "🔴" otherwise, 
           "⚪" if an error occurred.
    """
    try:
        # Fetch WHOIS data for the domain
        whois_data = whois.whois(domain)

        # Common indicators of privacy protection in WHOIS data
        privacy_indicators = [
            'privacy', 'protected', 'redacted', 'whoisguard', 'domains by proxy',
            'anonymous', 'contact privacy', 'whois privacy', 'perfect privacy', 'data protected'
        ]

        # Fields that might contain privacy-related information
        fields_to_check = [
            'registrar', 'tech_email', 'admin_email', 'registrant_email', 
            'org', 'name', 'address'
        ]

        # Check for privacy indicators in relevant WHOIS fields
        for field in fields_to_check:
            field_value = whois_data.get(field, '')
            if any(indicator in str(field_value).lower() for indicator in privacy_indicators):
                return "🟢"

        return "🔴"

    except WhoisCommandFailed as e:
        print(f"WHOIS command failed for {domain}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An error occurred while checking privacy-protected Whois for {domain}: {e}")
        return "⚪"
