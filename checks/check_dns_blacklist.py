import dns.resolver
from dns.resolver import NXDOMAIN, NoAnswer, Timeout, NoNameservers

def check_dns_blacklist(domain: str) -> str:
    """
    Check if a domain is blacklisted in known DNS-based blacklists.

    Args:
        domain (str): The domain name to be checked.

    Returns:
        str: 
            - "🟢" if the domain is not in any blacklist.
            - "🔴" if the domain is found in a blacklist.
    """
    
    # Set of DNS blacklists to check against
    blacklists = {
        "zen.spamhaus.org",
        "bl.spamcop.net"
        # Add more blacklists as needed
    }

    # Iterate over each blacklist to check the domain
    for blacklist in blacklists:
        try:
            # Query the blacklist with the domain
            query = f"{domain}.{blacklist}"
            dns.resolver.resolve(query, 'A')
            print(f"Domain {domain} is listed in {blacklist}.")
            return "🔴"
        
        except NXDOMAIN:
            # The domain is not listed in this blacklist
            continue  
        except NoAnswer:
            print(f"No answer received from {blacklist}. It might be down or not reachable.")
            continue
        except Timeout:
            print(f"Request to {blacklist} timed out.")
            continue
        except NoNameservers:
            print(f"No name servers available for {blacklist}.")
            continue
        except Exception as e:
            print(f"An unexpected error occurred while checking {domain} against {blacklist}: {e}")
            continue

    # If no blacklists returned a positive result
    print(f"Domain {domain} is not listed in any blacklists.")
    return "🟢"
