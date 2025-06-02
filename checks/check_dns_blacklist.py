import dns.resolver
import logging
from dns.resolver import NXDOMAIN, NoAnswer, Timeout, NoNameservers
from urllib.parse import urlparse
import re
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

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
            - "⚪" if errors occurred during checking.
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
        "cbl.abuseat.org": {"priority": "important", "type": "malware", "ignore_pbl": False},
        
        # Policy blacklists (often shared hosting - less critical for websites)
        "pbl.spamhaus.org": {"priority": "policy", "type": "policy", "ignore_pbl": False},
        
        # Important spam blacklists
        "dnsbl.sorbs.net": {"priority": "important", "type": "spam", "ignore_pbl": False},
        "b.barracudacentral.org": {"priority": "important", "type": "spam", "ignore_pbl": False},
        
        # Additional checks
        "dnsbl.dronebl.org": {"priority": "additional", "type": "proxy", "ignore_pbl": False},
    }

    def check_single_blacklist(blacklist_info):
        """Helper function to check a single blacklist"""
        blacklist, info = blacklist_info
        try:
            # Get IP address of domain first
            ip_address = socket.gethostbyname(domain)
            
            # Skip private/local IP addresses
            if ip_address.startswith(('127.', '192.168.', '10.')) or ip_address.startswith('172.'):
                if int(ip_address.split('.')[1]) in range(16, 32):  # 172.16-31.x.x
                    return {
                        "blacklist": blacklist,
                        "listed": False,
                        "priority": info["priority"],
                        "type": info["type"],
                        "skip_reason": "Private IP"
                    }
            
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
            
            # For zen.spamhaus.org, check the return code to filter out PBL entries
            if blacklist == "zen.spamhaus.org" and info.get("ignore_pbl"):
                for rdata in result:
                    return_code = str(rdata)
                    # Spamhaus return codes: 127.0.0.2-127.0.0.3 are PBL (policy, not actual spam)
                    if return_code in ['127.0.0.2', '127.0.0.3']:
                        return {
                            "blacklist": blacklist,
                            "listed": False,  # Treat PBL as not listed for website checks
                            "priority": "policy",
                            "type": "policy",
                            "ip": ip_address,
                            "return_code": return_code,
                            "note": "PBL listing (shared hosting policy, not spam)"
                        }
            
            return {
                "blacklist": blacklist,
                "listed": True,
                "priority": info["priority"],
                "type": info["type"],
                "ip": ip_address
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
        except socket.gaierror:
            logger.error(f"Could not resolve IP for domain {domain}")
            return {
                "blacklist": blacklist,
                "listed": None,
                "priority": info["priority"],
                "type": info["type"],
                "error": "Domain resolution failed"
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
            return "🔴"
        elif len(important_threats) >= 2:
            logger.error(f"Domain {domain} found in multiple threat blacklists")
            return "🔴"
        elif important_threats:
            logger.warning(f"Domain {domain} found in threat blacklists")
            return "🟡"
        elif policy_listings:
            logger.info(f"Domain {domain} IP in policy lists only (shared hosting)")
            return "🟢"  # Policy listings are not security threats
        else:
            logger.info(f"Domain {domain} not found in any blacklists")
            return "🟢"

    except Exception as e:
        logger.error(f"Unexpected error during blacklist checking for {domain}: {e}")
        return "⚪"
