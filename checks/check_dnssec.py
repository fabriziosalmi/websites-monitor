import dns.resolver

def check_dnssec(domain):
    """
    Check if a domain supports DNSSEC (Domain Name System Security Extensions).

    Args:
    - domain (str): The domain name to be checked.

    Returns:
    - str: "🟢" if the domain supports DNSSEC,
           "🔴" if the domain does not support DNSSEC or there's a DNSSEC-related error,
           "🟠" for other errors.
    """
    try:
        # Resolve and check if DNSSEC is enabled for the domain
        dns.resolver.resolve_and_check(domain, 'A')
        return "🟢"
    except dns.resolver.NoAnswer:
        print(f"No answer received for {domain}. It might be that the domain doesn't exist or there are connection issues.")
        return "🔴"
    except dns.resolver.NoNameservers:
        print(f"No name servers available for {domain}.")
        return "🔴"
    except dns.resolver.NXDOMAIN:
        print(f"The domain {domain} does not exist.")
        return "🔴"
    except dns.resolver.Timeout:
        print(f"Request to check DNSSEC for {domain} timed out.")
        return "🔴"
    except dns.dnssec.ValidationFailure:
        print(f"Validation failure while checking DNSSEC for {domain}.")
        return "🔴"
    except Exception as e:
        print(f"An unexpected error occurred while checking DNSSEC for {domain}: {e}")
        return "🟠"

