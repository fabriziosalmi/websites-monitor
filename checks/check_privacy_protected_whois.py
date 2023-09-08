import whois

def check_privacy_protected_whois(domain):
    """
    Check if a domain's WHOIS information indicates that it is privacy-protected.
    
    Args:
    - domain (str): The domain to check.
    
    Returns:
    - str: "🟢" if the domain's WHOIS information is privacy-protected, "🔴" otherwise.
    """
    
    try:
        whois_data = whois.whois(domain)
        
        # Fields that might contain privacy protection-related information
        fields_to_check = ['registrar', 'tech_email', 'admin_email', 'registrant_email']
        
        for field in fields_to_check:
            if 'privacy' in whois_data.get(field, '').lower():
                return "🟢"

        return "🔴"
    except Exception as e:
        print(f"An error occurred while checking privacy-protected Whois for {domain}: {e}")
        return "⚪"
