import dns.resolver
import logging
from dns.resolver import NXDOMAIN, NoAnswer, Timeout, NoNameservers
from urllib.parse import urlparse
import re
import socket
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

# Spamhaus ZEN return codes:
# 127.0.0.2-127.0.0.9 are SBL/CSS/XBL/DROP listings, 127.0.0.10-11 are PBL
# (policy: end-user ranges that should not send mail directly, not a threat).
ZEN_LISTED_CODES = {f"127.0.0.{i}" for i in range(2, 10)}
ZEN_POLICY_CODES = {"127.0.0.10", "127.0.0.11"}


def interpret_dnsbl_answer(blacklist: str, codes) -> str:
    """
    Interpret the A records returned by a DNSBL for a reversed-IP query.

    Returns:
        "listed"  if the answer is a real listing,
        "policy"  if it is a Spamhaus PBL (policy) listing,
        "error"   if the answer is an error code and says nothing about the IP.

    Answers in 127.255.255.0/24 are error codes (Spamhaus: 252 typo in the
    zone name, 254 query through a public/open resolver, 255 rate limited).
    Answers outside 127.0.0.0/8 (e.g. NXDOMAIN hijacking resolvers) and
    127.0.0.1 are not valid listing codes either.
    """
    codes = [str(c) for c in codes]
    if not codes:
        return "error"
    if any(not c.startswith("127.0.0.") or c == "127.0.0.1" for c in codes):
        return "error"
    if blacklist == "zen.spamhaus.org":
        if any(c in ZEN_LISTED_CODES for c in codes):
            return "listed"
        if any(c in ZEN_POLICY_CODES for c in codes):
            return "policy"
        return "error"
    return "listed"


def check_dns_blacklist(domain: str) -> str:
    """
    Check if a domain is blacklisted in known DNS-based blacklists.

    Args:
        domain (str): The domain name to be checked.

    Returns:
        str: 
            - "🟢" if the domain is not in any blacklist.
            - "🟡" if the domain is found in some blacklists.
            - "🔴" if the domain is found in multiple or critical blacklists.
            - "⚪" if no blacklist could give a verdict (or the IP is not public).
            A "(no verdict from ...)" suffix names lists that answered with an
            error code (e.g. Spamhaus 127.255.255.254 when queried through a
            public resolver); those lists are not counted as listings.

    Note: these are IP-based DNSBLs. The domain's IPv4 address is queried,
    so for a site behind a CDN the result describes the CDN edge IP.
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

    # Enhanced blacklist collection with more accurate categorization
    blacklists = {
        # Critical malware/spam blacklists (actual threats)
        "zen.spamhaus.org": {"priority": "critical", "type": "spam", "ignore_pbl": True},
        "bl.spamcop.net": {"priority": "critical", "type": "spam", "ignore_pbl": False},
        
        # Policy blacklists (often shared hosting - less critical for websites)
        "pbl.spamhaus.org": {"priority": "policy", "type": "policy", "ignore_pbl": False},
        
        # Important spam blacklists
        "dnsbl.sorbs.net": {"priority": "important", "type": "spam", "ignore_pbl": False},
        "b.barracudacentral.org": {"priority": "important", "type": "spam", "ignore_pbl": False},
        
        # Additional checks
        "dnsbl.dronebl.org": {"priority": "additional", "type": "proxy", "ignore_pbl": False},
    }

    # These are IP-based lists: query the domain's IPv4 address, not the name.
    try:
        ip_address = socket.gethostbyname(domain)
    except socket.gaierror:
        logger.error(f"Could not resolve IP for domain {domain}")
        return "⚪ (domain does not resolve)"

    # Skip private/local IP addresses, DNSBLs say nothing about them
    if not ipaddress.ip_address(ip_address).is_global:
        logger.info(f"Domain {domain} resolves to non-public IP {ip_address}, skipping DNSBL checks")
        return "⚪ (non-public IP)"

    def check_single_blacklist(blacklist_info):
        """Helper function to check a single blacklist"""
        blacklist, info = blacklist_info
        try:
            # Reverse IP for blacklist query
            ip_parts = ip_address.split('.')
            reversed_ip = '.'.join(reversed(ip_parts))
            
            # Query the blacklist with custom resolver for timeout
            query = f"{reversed_ip}.{blacklist}"
            
            # Create custom resolver with timeout
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5
            
            result = resolver.resolve(query, 'A')
            return_codes = [str(rdata) for rdata in result]
            verdict = interpret_dnsbl_answer(blacklist, return_codes)

            if verdict == "error":
                # Error code (e.g. 127.255.255.254: query via public resolver)
                logger.warning(f"Blacklist {blacklist} answered error code {return_codes} for {ip_address}, no verdict")
                return {
                    "blacklist": blacklist,
                    "listed": None,  # Unknown: the list refused to answer
                    "priority": info["priority"],
                    "type": info["type"],
                    "ip": ip_address,
                    "return_code": return_codes,
                    "error": f"error code {', '.join(return_codes)}"
                }

            if verdict == "policy" and info.get("ignore_pbl"):
                return {
                    "blacklist": blacklist,
                    "listed": False,  # Treat PBL as not listed for website checks
                    "priority": "policy",
                    "type": "policy",
                    "ip": ip_address,
                    "return_code": return_codes,
                    "note": "PBL listing (shared hosting policy, not spam)"
                }

            return {
                "blacklist": blacklist,
                "listed": True,
                "priority": info["priority"],
                "type": info["type"],
                "ip": ip_address,
                "return_code": return_codes
            }
            
        except NXDOMAIN:
            # Domain not listed in this blacklist (good)
            return {
                "blacklist": blacklist,
                "listed": False,
                "priority": info["priority"],
                "type": info["type"]
            }
        except (NoAnswer, Timeout, NoNameservers) as e:
            logger.debug(f"DNS issue with blacklist {blacklist}: {e}")
            return {
                "blacklist": blacklist,
                "listed": None,  # Unknown due to error
                "priority": info["priority"],
                "type": info["type"],
                "error": str(e)
            }
        except Exception as e:
            logger.debug(f"Error checking {blacklist}: {e}")
            return {
                "blacklist": blacklist,
                "listed": None,
                "priority": info["priority"],
                "type": info["type"],
                "error": str(e)
            }

    try:
        # Performance optimization - concurrent checking
        results = []
        with ThreadPoolExecutor(max_workers=3) as executor:  # Reduced workers to be gentler
            futures = {executor.submit(check_single_blacklist, item): item for item in blacklists.items()}
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error in blacklist check thread: {e}")

        # Analyze results with improved scoring that ignores policy listings
        actual_threats = [r for r in results if r["listed"] is True and r["type"] not in ["policy"]]
        policy_listings = [r for r in results if r["listed"] is True and r["type"] == "policy"]
        
        unknown = sorted(r["blacklist"] for r in results if r["listed"] is None)
        if results and len(unknown) == len(results):
            logger.error(f"No blacklist gave a verdict for {domain}")
            return "⚪ (no blacklist answered)"
        note = f" (no verdict from {', '.join(unknown)})" if unknown else ""

        critical_threats = [r for r in actual_threats if r["priority"] == "critical"]
        important_threats = [r for r in actual_threats if r["priority"] == "important"]
        
        # Log actual threats only
        for result in actual_threats:
            logger.warning(f"Domain {domain} listed in {result['blacklist']} ({result['type']}, {result['priority']})")
        
        # Log policy listings as info (not warnings)
        for result in policy_listings:
            logger.info(f"Domain {domain} IP in policy list {result['blacklist']} (shared hosting policy)")
        
        # Improved categorization - only consider actual threats
        if critical_threats:
            logger.critical(f"Domain {domain} found in {len(critical_threats)} critical threat blacklists")
            return "🔴" + note
        elif len(important_threats) >= 2:
            logger.error(f"Domain {domain} found in multiple threat blacklists")
            return "🔴" + note
        elif important_threats:
            logger.warning(f"Domain {domain} found in threat blacklists")
            return "🟡" + note
        elif policy_listings:
            logger.info(f"Domain {domain} IP in policy lists only (shared hosting)")
            return "🟢" + note  # Policy listings are not security threats
        else:
            logger.info(f"Domain {domain} not found in any blacklists")
            return "🟢" + note

    except Exception as e:
        logger.error(f"Unexpected error during blacklist checking for {domain}: {e}")
        return "⚪"
