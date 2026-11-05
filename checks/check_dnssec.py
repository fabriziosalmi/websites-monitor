import dns.resolver
import dns.dnssec
import dns.query
import dns.name
import dns.rdatatype
import dns.flags
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
        # Resolver failures (SERVFAIL/REFUSED/timeout) on individual queries.
        # They must not abort the whole check, but if every query failed we
        # cannot give a verdict.
        resolver_errors = []

        # Check for DNSKEY records
        try:
            dnskey_query = dns.resolver.resolve(domain_name, 'DNSKEY', tcp=True)
            if dnskey_query:
                dnssec_indicators.append("DNSKEY records found")
                logger.info(f"Found {len(dnskey_query)} DNSKEY records for {domain}")
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            logger.warning(f"No DNSKEY records found for {domain}")
        except (dns.resolver.NoNameservers, dns.resolver.LifetimeTimeout) as e:
            resolver_errors.append(f"DNSKEY: {e}")

        # Check for DS records in parent zone
        try:
            ds_query = dns.resolver.resolve(domain_name, 'DS', tcp=True)
            if ds_query:
                dnssec_indicators.append("DS records found")
                logger.info(f"Found {len(ds_query)} DS records for {domain}")
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            logger.warning(f"No DS records found for {domain}")
        except (dns.resolver.NoNameservers, dns.resolver.LifetimeTimeout) as e:
            resolver_errors.append(f"DS: {e}")

        # Check for RRSIG records (signature records).
        # Querying qtype RRSIG directly is answered with SERVFAIL by most
        # recursive resolvers (1.1.1.1, 8.8.8.8, Docker/Tailscale stubs), so
        # ask for the A record with the DO bit set and look for the RRSIG
        # that covers it in the answer section.
        try:
            resolver = dns.resolver.Resolver()
            resolver.use_edns(0, dns.flags.DO, 4096)  # Enable DNSSEC
            a_query = resolver.resolve(domain_name, 'A', tcp=True)
            if any(rrset.rdtype == dns.rdatatype.RRSIG for rrset in a_query.response.answer):
                dnssec_indicators.append("RRSIG records found")
                logger.info(f"Found RRSIG records for {domain}")
            else:
                logger.warning(f"No RRSIG records found for {domain}")
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            logger.warning(f"No RRSIG records found for {domain}")
        except (dns.resolver.NoNameservers, dns.resolver.LifetimeTimeout) as e:
            resolver_errors.append(f"A+DO: {e}")

        if not dnssec_indicators and len(resolver_errors) == 3:
            logger.error(f"All DNSSEC queries failed for {domain}: {'; '.join(resolver_errors)}")
            return "⚪"

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
