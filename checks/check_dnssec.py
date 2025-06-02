import dns.resolver
import dns.dnssec
import dns.query
import dns.name
import dns.rdatatype
import logging
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def check_dnssec(domain: str) -> str:
    """
    Check if a domain supports DNSSEC (Domain Name System Security Extensions).

    Args:
        domain (str): The domain name to be checked.

    Returns:
        str:
            - "🟢" if the domain supports DNSSEC properly.
            - "🟡" if DNSSEC is partially configured.
            - "🔴" if the domain does not support DNSSEC or there's a DNSSEC-related error.
            - "⚪" for other errors.
    """
    # Input validation and normalization
    if not domain:
        logger.error("Domain is required")
        return "⚪"
    
    # Normalize domain
    domain = domain.lower().strip()
    domain = re.sub(r'^https?://', '', domain)
    domain = re.sub(r'^www\.', '', domain)
    domain = domain.split('/')[0]  # Remove path if present
    domain = domain.split(':')[0]  # Remove port if present
    
    # Validate domain format
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]$', domain):
        logger.error(f"Invalid domain format: {domain}")
        return "⚪"

    try:
        # Convert domain to DNS name object
        domain_name = dns.name.from_text(domain)
        
        # Enhanced detection patterns
        dnssec_indicators = []
        
        # Check for DNSKEY records
        try:
            dnskey_query = dns.resolver.resolve(domain_name, 'DNSKEY', tcp=True)
            if dnskey_query:
                dnssec_indicators.append("DNSKEY records found")
                logger.info(f"Found {len(dnskey_query)} DNSKEY records for {domain}")
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            logger.warning(f"No DNSKEY records found for {domain}")
        
        # Check for DS records in parent zone
        try:
            ds_query = dns.resolver.resolve(domain_name, 'DS', tcp=True)
            if ds_query:
                dnssec_indicators.append("DS records found")
                logger.info(f"Found {len(ds_query)} DS records for {domain}")
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            logger.warning(f"No DS records found for {domain}")
        
        # Check for RRSIG records (signature records)
        try:
            rrsig_query = dns.resolver.resolve(domain_name, 'RRSIG', tcp=True)
            if rrsig_query:
                dnssec_indicators.append("RRSIG records found")
                logger.info(f"Found RRSIG records for {domain}")
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            logger.warning(f"No RRSIG records found for {domain}")
        
        # Fallback mechanism - check for any DNSSEC records
        if not dnssec_indicators:
            # Try checking A record with DNSSEC validation
            try:
                resolver = dns.resolver.Resolver()
                resolver.use_edns(0, dns.flags.DO, 4096)  # Enable DNSSEC
                a_query = resolver.resolve(domain_name, 'A')
                # If we get here, DNS works but DNSSEC might not be configured
                logger.info(f"DNS resolution works for {domain} but no DNSSEC indicators found")
            except Exception:
                pass
        
        # Improved scoring and categorization
        if len(dnssec_indicators) >= 2:
            logger.info(f"Strong DNSSEC configuration for {domain}: {', '.join(dnssec_indicators)}")
            return "🟢"
        elif len(dnssec_indicators) == 1:
            logger.warning(f"Partial DNSSEC configuration for {domain}: {dnssec_indicators[0]}")
            return "🟡"
        else:
            logger.warning(f"No DNSSEC configuration found for {domain}")
            return "🔴"

    except dns.resolver.NoAnswer:
        logger.warning(f"No DNS answer received for {domain} - domain might not exist or have DNS issues")
        return "⚪"
    except dns.resolver.NoNameservers:
        logger.error(f"No name servers available for {domain}")
        return "⚪"
    except dns.resolver.NXDOMAIN:
        logger.error(f"Domain {domain} does not exist")
        return "⚪"
    except dns.resolver.Timeout:
        logger.error(f"DNS request timeout while checking DNSSEC for {domain}")
        return "⚪"
    except dns.dnssec.ValidationFailure as e:
        logger.error(f"DNSSEC validation failure for {domain}: {e}")
        return "🔴"
    except Exception as e:
        logger.error(f"Unexpected error while checking DNSSEC for {domain}: {e}")
        return "⚪"
