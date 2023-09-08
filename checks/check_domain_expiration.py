from datetime import datetime
import whois

def check_domain_expiration(domain):
    """
    Check the expiration date of a domain.

    Args:
    - domain (str): The domain name to be checked.

    Returns:
    - str: "🟢" if the domain has more than 30 days to expire,
           "🟠" if the domain has between 15 to 30 days to expire,
           "🔴" if the domain has less than 15 days to expire or there's an expiration-related error,
           "⚪" for other errors.
    """

    def get_days_to_expire(exp_date):
        """Calculate the days remaining for expiration."""
        if not exp_date:
            return None
        if isinstance(exp_date, list):
            exp_date = exp_date[0]
        return (exp_date - datetime.now()).days

    try:
        w = whois.whois(domain)
        days_to_expire = get_days_to_expire(w.expiration_date)
        
        if days_to_expire is None:
            print(f"Couldn't retrieve expiration details for {domain}.")
            return "🔴"
        elif days_to_expire < 15:
            return "🔴"
        elif days_to_expire < 30:
            return "🟠"
        else:
            return "🟢"
    except Exception as e:
        print(f"An error occurred while checking domain expiration for {domain}: {e}")
        return "⚪"
