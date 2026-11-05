from datetime import datetime, timedelta, timezone
import whois
import logging
import re
from urllib.parse import urlparse
try:
    from whois.parser import PywhoisError
except ImportError:
    from whois import WhoisError as PywhoisError

logger = logging.getLogger(__name__)


def _to_utc(value):
    """
    Convert a WHOIS date (datetime or string) to an aware UTC datetime.

    python-whois may return aware datetimes, naive datetimes or strings.
    Naive values are assumed to be UTC. Returns None if unparseable.
    """
    if isinstance(value, str):
        text = value.strip()
        parsed = None
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
            try:
                parsed = datetime.strptime(text, fmt)
                break
            except ValueError:
                continue
        if parsed is None:
            try:
                parsed = datetime.fromisoformat(text.replace('Z', '+00:00'))
            except ValueError:
                return None
        value = parsed
    if not isinstance(value, datetime):
        return None
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def check_domain_expiration(domain: str) -> str:
    """
    Check the expiration date of a domain.

    Args:
        domain (str): The domain name to be checked.

    Returns:
        str:
            - "🟢 (X days left)" if the domain has more than 90 days to expire.
            - "🟡 (X days left)" if the domain has between 30 to 90 days to expire.
            - "🟠 (X days left)" if the domain has between 15 to 30 days to expire.
            - "🔴 (X days left)" if the domain has less than 15 days to expire.
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

    def get_days_to_expire(exp_date):
        """Calculate the days remaining for expiration."""
        if not exp_date:
            return None

        # Handle list of dates (some registrars return multiple dates).
        # Normalize every entry first: a list may mix naive and aware values.
        if isinstance(exp_date, list):
            dates = [d for d in (_to_utc(item) for item in exp_date) if d is not None]
            if not dates:
                return None
            # Use the earliest expiration date
            exp_date = min(dates)
        else:
            exp_date = _to_utc(exp_date)
            if exp_date is None:
                return None

        return (exp_date - datetime.now(timezone.utc)).days

    try:
        # Fetch WHOIS data for the domain with timeout
        logger.info(f"Fetching WHOIS data for {domain}")
        w = whois.whois(domain)
        
        if not w:
            logger.error(f"No WHOIS data returned for {domain}")
            return "⚪"
        
        # Enhanced detection patterns
        expiration_date = w.expiration_date
        creation_date = w.creation_date
        
        days_to_expire = get_days_to_expire(expiration_date)

        if days_to_expire is None:
            logger.error(f"Could not retrieve or parse expiration date for {domain}")
            return "⚪"

        # Log additional domain information
        if creation_date:
            creation_days = get_days_to_expire(creation_date)
            if creation_days:
                domain_age = abs(creation_days)
                logger.info(f"Domain {domain} is {domain_age} days old")

        # Improved scoring and categorization
        if days_to_expire < 0:
            logger.critical(f"Domain {domain} has already expired {abs(days_to_expire)} days ago!")
            return f"🔴 (expired {abs(days_to_expire)} days ago)"
        elif days_to_expire < 15:
            logger.critical(f"Domain {domain} expires in {days_to_expire} days - URGENT!")
            return f"🔴 ({days_to_expire} days left)"
        elif days_to_expire < 30:
            logger.warning(f"Domain {domain} expires in {days_to_expire} days - action needed soon")
            return f"🟠 ({days_to_expire} days left)"
        elif days_to_expire < 90:
            logger.info(f"Domain {domain} expires in {days_to_expire} days - consider renewal")
            return f"🟡 ({days_to_expire} days left)"
        else:
            logger.info(f"Domain {domain} expires in {days_to_expire} days - safe")
            return f"🟢 ({days_to_expire} days left)"
            
    except PywhoisError as e:
        logger.error(f"WHOIS parsing error for {domain}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error while checking domain expiration for {domain}: {e}")
        return "⚪"
