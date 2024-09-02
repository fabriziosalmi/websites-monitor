from datetime import datetime
import whois

def check_domain_expiration(domain: str) -> str:
    """
    Check the expiration date of a domain.

    Args:
        domain (str): The domain name to be checked.

    Returns:
        str:
            - "🟢 (X days left)" if the domain has more than 30 days to expire.
            - "🟠 (X days left)" if the domain has between 15 to 30 days to expire.
            - "🔴 (X days left)" if the domain has less than 15 days to expire.
            - "⚪" for other errors, where X is the number of days until expiration.
    """

    def get_days_to_expire(exp_date):
        """Calculate the days remaining for expiration."""
        if not exp_date:
            return None
        if isinstance(exp_date, list):
            exp_date = exp_date[0]
        return (exp_date - datetime.now()).days

    try:
        # Fetch WHOIS data for the domain
        w = whois.whois(domain)
        days_to_expire = get_days_to_expire(w.expiration_date)

        if days_to_expire is None:
            print(f"Couldn't retrieve expiration details for {domain}.")
            return "⚪"
        elif days_to_expire < 15:
            print(f"Domain {domain} is expiring soon! Only {days_to_expire} days left.")
            return f"🔴 ({days_to_expire} days left)"
        elif 15 <= days_to_expire < 30:
            print(f"Domain {domain} is expiring in {days_to_expire} days.")
            return f"🟠 ({days_to_expire} days left)"
        else:
            print(f"Domain {domain} is safe with {days_to_expire} days left.")
            return f"🟢 ({days_to_expire} days left)"
    except whois.parser.PywhoisError:
        print(f"WHOIS data could not be fetched for {domain}. Domain may not be registered.")
        return "⚪"
    except Exception as e:
        print(f"An error occurred while checking domain expiration for {domain}: {e}")
        return "⚪"
