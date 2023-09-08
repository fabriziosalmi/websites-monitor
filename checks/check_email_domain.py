import dns.resolver

def check_email_domain(email_domain):
    """
    Check if an email domain has an SPF record.

    Args:
    - email_domain (str): The domain of the email to be checked.

    Returns:
    - str: "🟢" if an SPF record is found,
           "🔴" if no SPF record is found,
           "⚪" for any other errors or issues.
    """

    try:
        answers = dns.resolver.resolve(email_domain, 'TXT')
        if any("v=spf1" in str(rdata) for rdata in answers):
            return "🟢"
        else:
            return "🔴"
    except dns.resolver.NXDOMAIN:
        print(f"{email_domain} does not exist.")
        return "🔴"
    except dns.resolver.NoAnswer:
        print(f"{email_domain} does not have a TXT record.")
        return "🔴"
    except Exception as e:
        print(f"An error occurred while checking email domain for {email_domain}: {e}")
        return "⚪"
