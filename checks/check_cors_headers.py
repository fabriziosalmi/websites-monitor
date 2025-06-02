import requests
import logging
from requests.exceptions import RequestException, HTTPError
from urllib.parse import urlparse
import re

logger = logging.getLogger(__name__)

def check_cors_headers(website: str) -> str:
    """
    Checks the CORS policy of the given website.

    Args:
        website (str): The website URL to check.

    Returns:
        str: 
            - "🟢" if the CORS policy is secure and properly configured.
            - "🟡" if CORS is configured but with potential security concerns.
            - "🔴" if the CORS policy is insecure or misconfigured.
            - "⚪" if an error occurred during checking.
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
        'User-Agent': 'CORSPolicyChecker/2.0',
        'Origin': 'https://example.com'  # Test with a different origin
    }

    try:
        # Enhanced detection patterns - check multiple endpoints and methods
        endpoints_to_check = [
            website,
            f"{website}/api",
            f"{website}/api/v1", 
            f"{website}/graphql"
        ]
        
        cors_findings = []
        
        for endpoint in endpoints_to_check:
            try:
                # Check OPTIONS request (preflight)
                options_response = requests.options(endpoint, headers=headers, timeout=10)
                
                # Check GET request for CORS headers
                get_response = requests.get(endpoint, headers=headers, timeout=10)
                
                for response in [options_response, get_response]:
                    if response.status_code < 400:  # Only check successful responses
                        cors_analysis = analyze_cors_headers(response.headers, endpoint)
                        if cors_analysis:
                            cors_findings.append(cors_analysis)
                            
            except RequestException:
                continue  # Skip endpoints that don't respond
        
        if not cors_findings:
            logger.info(f"No CORS headers found for {website} - may not support CORS")
            return "🟢"
        
        # Improved scoring and categorization
        critical_issues = [f for f in cors_findings if f["risk"] == "critical"]
        high_issues = [f for f in cors_findings if f["risk"] == "high"] 
        medium_issues = [f for f in cors_findings if f["risk"] == "medium"]
        
        # Log findings
        for finding in cors_findings[:5]:  # Log first 5 findings
            level = logger.critical if finding["risk"] == "critical" else logger.warning
            level(f"CORS issue on {finding['endpoint']}: {finding['issue']}")
        
        if critical_issues:
            logger.critical(f"Critical CORS vulnerabilities found on {website}")
            return "🔴"
        elif high_issues or len(medium_issues) >= 2:
            logger.warning(f"CORS security concerns found on {website}")
            return "🟡"
        elif medium_issues:
            logger.info(f"Minor CORS configuration issues found on {website}")
            return "🟡"
        else:
            logger.info(f"CORS policy appears secure for {website}")
            return "🟢"

    except (HTTPError, RequestException) as e:
        logger.error(f"Request error while checking CORS headers for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error while checking CORS headers for {website}: {e}")
        return "⚪"

def analyze_cors_headers(headers, endpoint):
    """Helper function to analyze CORS headers for security issues"""
    cors_origin = headers.get('Access-Control-Allow-Origin', '')
    cors_credentials = headers.get('Access-Control-Allow-Credentials', '').lower()
    cors_methods = headers.get('Access-Control-Allow-Methods', '')
    cors_headers_allowed = headers.get('Access-Control-Allow-Headers', '')
    
    # Critical security issues
    if cors_origin == '*' and cors_credentials == 'true':
        return {
            "endpoint": endpoint,
            "issue": "Wildcard origin with credentials allowed - critical security risk",
            "risk": "critical"
        }
    
    # High risk issues
    if cors_origin == '*':
        return {
            "endpoint": endpoint, 
            "issue": "Wildcard CORS origin allows all domains",
            "risk": "high"
        }
    
    # Medium risk issues
    if 'DELETE' in cors_methods.upper() and cors_credentials == 'true':
        return {
            "endpoint": endpoint,
            "issue": "DELETE method allowed with credentials",
            "risk": "medium"
        }
    
    if '*' in cors_headers_allowed:
        return {
            "endpoint": endpoint,
            "issue": "Wildcard headers allowed",
            "risk": "medium" 
        }
    
    return None
