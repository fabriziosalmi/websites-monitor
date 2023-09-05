import whois

def check_privacy_protected_whois(domain):
    try:
        w = whois.whois(domain)
        if 'privacy' in w.get('registrar', '').lower() or 'privacy' in w.get('tech_email', '').lower():
            return "🟢"
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking privacy-protected Whois for {domain}: {e}")
        return "🔴"
