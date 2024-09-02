import dns.resolver
import dns.dnssec
import dns.query
import dns.name
import dns.rdatatype

def check_dnssec(domain: str) -> str:
    """
    Check if a domain supports DNSSEC (Domain Name System Security Extensions).

    Args:
        domain (str): The domain name to be checked.

    Returns:
        str:
            - "🟢" if the domain supports DNSSEC.
            - "🔴" if the domain does not support DNSSEC or there's a DNSSEC-related error.
            - "⚪" for other errors.
    """
    try:
        # Convert domain to DNS name object
        domain_name = dns.name.from_text(domain)
        
        # Retrieve the DNSKEY record for the domain
        dnskey_query = dns.resolver.resolve(domain_name, 'DNSKEY')
        
        # Check for the DS (Delegation Signer) record in the parent zone
        ds_query = dns.resolver.resolve(domain_name, 'DS')
        
        # Validate DNSSEC using the DNSKEY and DS records
        for rdata in ds_query:
            if dns.dnssec.validate(dnskey_query.rrset, rdata):
                print(f"DNSSEC is properly configured for {domain}.")
                return "🟢"
        
        print(f"DNSSEC is not configured correctly for {domain}.")
        return "🔴"

    except dns.resolver.NoAnswer:
        print(f"No answer received for {domain}. It might be that the domain doesn't exist or there are connection issues.")
        return "⚪"
    except dns.resolver.NoNameservers:
        print(f"No name servers available for {domain}.")
        return "⚪"
    except dns.resolver.NXDOMAIN:
        print(f"The domain {domain} does not exist.")
        return "⚪"
    except dns.resolver.Timeout:
        print(f"Request to check DNSSEC for {domain} timed out.")
        return "⚪"
    except dns.dnssec.ValidationFailure:
        print(f"Validation failure while checking DNSSEC for {domain}.")
        return "🔴"
    except Exception as e:
        print(f"An unexpected error occurred while checking DNSSEC for {domain}: {e}")
        return "⚪"
