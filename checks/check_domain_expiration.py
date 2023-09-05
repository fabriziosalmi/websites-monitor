from datetime import datetime
import whois

def check_domain_expiration(domain):
    try:
        w = whois.whois(domain)
        expiration_date = w.expiration_date
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]
        days_to_expire = (expiration_date - datetime.now()).days

        if days_to_expire < 15:
            return "🔴"
        elif days_to_expire < 30:
            return "🟠"
        else:
            return "🟢"
    except Exception as e:
        print(f"An error occurred while checking domain expiration for {domain}: {e}")
        return "🔴"
