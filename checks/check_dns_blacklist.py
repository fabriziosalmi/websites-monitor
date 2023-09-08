import dns.resolver

def check_dns_blacklist(domain):
    """
    Check if a domain is blacklisted in known DNS-based blacklists.

    Args:
    - domain (str): The domain name to be checked.

    Returns:
    - str: "🟢" if the domain is not in any blacklist,
           "🔴" if the domain is found in a blacklist.
    """
    
    # Set of DNS blacklists
    blacklists = {
        "zen.spamhaus.org",
        "bl.spamcop.net"
        # ... You can add more blacklists here
    }

    for blacklist in blacklists:
        try:
            dns.resolver.query(f"{domain}.{blacklist}", 'A')
            print(f"Domain {domain} is listed in {blacklist}.")
            return "🔴"
        except dns.resolver.NXDOMAIN:
            continue  # The domain is not blacklisted in this blacklist
        except dns.resolver.NoAnswer:
            print(f"No answer received from {blacklist}. It might be down or not reachable.")
            continue
        except dns.resolver.Timeout:
            print(f"Request to {blacklist} timed out.")
            continue
        except dns.resolver.NoNameservers:
            print(f"No name servers available for {blacklist}.")
            continue
    return "🟢"
