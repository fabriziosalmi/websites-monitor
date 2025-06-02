import requests
import logging
from requests.exceptions import RequestException, Timeout, HTTPError
from urllib.parse import urlparse
import re

logger = logging.getLogger(__name__)

def check_cookie_samesite_attribute(website: str) -> str:
    """
    Verify the SameSite attribute of cookies for the website.

    Args:
        website (str): URL of the website to be checked.

    Returns:
        str:
            - "🟢" if all cookies have proper SameSite attributes
            - "🟡" if cookies have suboptimal but acceptable SameSite configuration
            - "🔴" if cookies have insecure SameSite configuration
            - "⚪" for any errors
    """
    # Input validation and URL normalization
    if not website:
        logger.error("Website URL is required")
        return "⚪"
    
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"
    
    try:
        parsed_url = urlparse(website)
        if not parsed_url.netloc:
            logger.error(f"Invalid URL format: {website}")
            return "⚪"
    except Exception as e:
        logger.error(f"URL parsing error for {website}: {e}")
        return "⚪"

    headers = {
        'User-Agent': 'SameSiteCookieChecker/2.0'
    }

    try:
        # Enhanced detection patterns - check multiple pages that might set cookies
        endpoints_to_check = [
            website,
            f"{website}/login",
            f"{website}/auth",
            f"{website}/api/auth",
            f"{website}/user/login"
        ]
        
        all_cookies = {}
        cookie_issues = []
        
        for endpoint in endpoints_to_check:
            try:
                response = requests.get(endpoint, headers=headers, timeout=10, allow_redirects=True)
                
                # Collect cookies from response
                for cookie in response.cookies:
                    cookie_name = cookie.name
                    if cookie_name not in all_cookies:
                        all_cookies[cookie_name] = {
                            'domain': cookie.domain,
                            'secure': cookie.secure,
                            'httponly': hasattr(cookie, 'httponly') and cookie.httponly,
                            'samesite': getattr(cookie, 'samesite', None),
                            'path': cookie.path,
                            'expires': cookie.expires,
                            'found_on': endpoint
                        }
                
            except RequestException:
                continue  # Skip endpoints that don't respond
        
        # If no cookies found, it's not necessarily a problem
        if not all_cookies:
            logger.info(f"No cookies found for {website}")
            return "🟢"
        
        logger.info(f"Found {len(all_cookies)} unique cookies for {website}")
        
        # Enhanced analysis of cookie security
        for cookie_name, cookie_info in all_cookies.items():
            samesite = cookie_info.get('samesite')
            secure = cookie_info.get('secure', False)
            httponly = cookie_info.get('httponly', False)
            
            # Critical security issues
            if samesite is None:
                if parsed_url.scheme == 'https':
                    cookie_issues.append({
                        "cookie": cookie_name,
                        "issue": "Missing SameSite attribute on HTTPS site",
                        "risk": "high",
                        "recommendation": "Add SameSite=Strict or SameSite=Lax"
                    })
                else:
                    cookie_issues.append({
                        "cookie": cookie_name,
                        "issue": "Missing SameSite attribute",
                        "risk": "medium",
                        "recommendation": "Add SameSite=Strict or SameSite=Lax"
                    })
            
            elif samesite and samesite.lower() == "none":
                if not secure:
                    cookie_issues.append({
                        "cookie": cookie_name,
                        "issue": "SameSite=None without Secure flag",
                        "risk": "critical",
                        "recommendation": "Add Secure flag when using SameSite=None"
                    })
                else:
                    cookie_issues.append({
                        "cookie": cookie_name,
                        "issue": "SameSite=None may allow CSRF attacks",
                        "risk": "medium",
                        "recommendation": "Consider using SameSite=Strict or Lax if cross-site access not needed"
                    })
            
            # Additional security checks
            if not secure and parsed_url.scheme == 'https':
                cookie_issues.append({
                    "cookie": cookie_name,
                    "issue": "Cookie not marked as Secure on HTTPS site",
                    "risk": "medium",
                    "recommendation": "Add Secure flag to prevent transmission over HTTP"
                })
            
            if not httponly and cookie_name.lower() in ['session', 'sessionid', 'auth', 'token']:
                cookie_issues.append({
                    "cookie": cookie_name,
                    "issue": "Authentication cookie not marked HttpOnly",
                    "risk": "high", 
                    "recommendation": "Add HttpOnly flag to prevent XSS access"
                })

        # Improved scoring and categorization
        critical_issues = [issue for issue in cookie_issues if issue["risk"] == "critical"]
        high_issues = [issue for issue in cookie_issues if issue["risk"] == "high"]
        medium_issues = [issue for issue in cookie_issues if issue["risk"] == "medium"]
        
        # Log findings
        for issue in cookie_issues[:5]:  # Log first 5 issues
            level = logger.critical if issue["risk"] == "critical" else logger.warning
            level(f"Cookie security issue - {issue['cookie']}: {issue['issue']}")
            logger.info(f"  Recommendation: {issue['recommendation']}")
        
        if critical_issues:
            logger.critical(f"Critical cookie security issues found on {website}")
            return "🔴"
        elif high_issues or len(medium_issues) >= 3:
            logger.warning(f"Significant cookie security concerns on {website}")
            return "🔴"
        elif medium_issues:
            logger.info(f"Minor cookie security issues found on {website}")
            return "🟡"
        else:
            logger.info(f"Cookie security configuration appears good for {website}")
            return "🟢"

    except (Timeout, HTTPError) as e:
        logger.error(f"HTTP error while checking cookie SameSite for {website}: {e}")
        return "⚪"
    except RequestException as e:
        logger.error(f"Request error while checking cookie SameSite for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error while checking cookie SameSite for {website}: {e}")
        return "⚪"
