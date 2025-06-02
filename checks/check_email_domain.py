import dns.resolver
import logging
from dns.resolver import NXDOMAIN, NoAnswer, NoNameservers, Timeout
import re

logger = logging.getLogger(__name__)

def check_email_domain(email_domain: str) -> str:
    """
    Check if an email domain has an SPF (Sender Policy Framework) record.

    Args:
        email_domain (str): The domain of the email to be checked.

    Returns:
        str: 
            - "🟢" if a strong SPF record is found.
            - "🟡" if a basic SPF record is found.
            - "🔴" if no SPF record is found.
            - "⚪" for any other errors or issues.
    """
    # Input validation
    if not email_domain:
        logger.error("Email domain is required")
        return "⚪"
    
    # Normalize domain (remove protocol, www, etc.)
    email_domain = email_domain.lower().strip()
    email_domain = re.sub(r'^https?://', '', email_domain)
    email_domain = re.sub(r'^www\.', '', email_domain)
    email_domain = email_domain.split('/')[0]  # Remove path if present
    
    # Validate domain format
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.[a-zA-Z]{2,}$', email_domain):
        logger.error(f"Invalid domain format: {email_domain}")
        return "⚪"

    try:
        # Query DNS TXT records for the given email domain
        answers = dns.resolver.resolve(email_domain, 'TXT', timeout=10)

        # Enhanced detection patterns
        spf_records = []
        for rdata in answers:
            txt_record = str(rdata).strip('"')
            if txt_record.startswith("v=spf1"):
                spf_records.append(txt_record)

        if not spf_records:
            logger.warning(f"No SPF record found for {email_domain}")
            return "🔴"
        
        if len(spf_records) > 1:
            logger.warning(f"Multiple SPF records found for {email_domain} - this may cause issues")
        
        # Analyze SPF record quality
        spf_record = spf_records[0]
        logger.info(f"SPF record found for {email_domain}: {spf_record}")
        
        # Improved scoring and categorization
        strong_indicators = [
            '-all',  # Hard fail
            'include:',  # Include mechanism
            'mx',  # MX mechanism
        ]
        
        weak_indicators = [
            '~all',  # Soft fail
            '?all',  # Neutral
            '+all',  # Pass all (very permissive)
        ]
        
        strong_score = sum(1 for indicator in strong_indicators if indicator in spf_record)
        weak_score = sum(1 for indicator in weak_indicators if indicator in spf_record)
        
        if strong_score >= 2 and '-all' in spf_record:
            logger.info(f"Strong SPF configuration for {email_domain}")
            return "🟢"
        elif strong_score >= 1 or ('~all' in spf_record):
            logger.info(f"Basic SPF configuration for {email_domain}")
            return "🟡"
        else:
            logger.warning(f"Weak SPF configuration for {email_domain}")
            return "🟡"
    
    except NXDOMAIN:
        logger.error(f"Domain {email_domain} does not exist")
        return "⚪"
    except NoAnswer:
        logger.warning(f"Domain {email_domain} does not have TXT records")
        return "🔴"
    except NoNameservers:
        logger.error(f"No nameservers found for domain {email_domain}")
        return "⚪"
    except Timeout:
        logger.error(f"DNS query for {email_domain} timed out")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error while checking email domain {email_domain}: {e}")
        return "⚪"
