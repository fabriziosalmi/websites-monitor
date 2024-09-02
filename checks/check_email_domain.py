import dns.resolver
from dns.resolver import NXDOMAIN, NoAnswer, NoNameservers, Timeout

def check_email_domain(email_domain: str) -> str:
    """
    Check if an email domain has an SPF (Sender Policy Framework) record.

    Args:
        email_domain (str): The domain of the email to be checked.

    Returns:
        str: 
            - "🟢" if an SPF record is found.
            - "🔴" if no SPF record is found.
            - "⚪" for any other errors or issues.
    """
    try:
        # Query DNS TXT records for the given email domain
        answers = dns.resolver.resolve(email_domain, 'TXT')

        # Check if any TXT record contains an SPF entry
        for rdata in answers:
            if "v=spf1" in str(rdata):
                print(f"SPF record found for {email_domain}: {rdata}")
                return "🟢"
        
        print(f"No SPF record found for {email_domain}.")
        return "🔴"
    
    except NXDOMAIN:
        print(f"The domain {email_domain} does not exist.")
        return "⚪"
    except NoAnswer:
        print(f"The domain {email_domain} does not have a TXT record.")
        return "⚪"
    except NoNameservers:
        print(f"No nameservers found for the domain {email_domain}.")
        return "⚪"
    except Timeout:
        print(f"The DNS query for {email_domain} timed out.")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking the email domain {email_domain}: {e}")
        return "⚪"
