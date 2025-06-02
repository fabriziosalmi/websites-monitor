import requests
import logging
from requests.exceptions import RequestException, Timeout, HTTPError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_security_headers(website: str) -> str:
    """
    Check for the presence and correct implementation of recommended security headers on a website.

    Args:
        website (str): URL of the website to be checked.

    Returns:
        str:
            - "🟢" if all recommended headers are properly implemented.
            - "🟠" if headers are present but not all are ideally implemented.
            - "🔴" if some recommended headers are missing.
            - "⚪" for any errors.
    """
    # Input validation and URL normalization
    if not website or not isinstance(website, str):
        logger.error(f"Invalid website input: {website}")
        return "⚪"
    
    website = website.strip()
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Enhanced recommended security headers with scoring
    security_headers = {
        'X-Content-Type-Options': {'expected': 'nosniff', 'weight': 2},
        'X-XSS-Protection': {'expected': '1; mode=block', 'weight': 2},
        'Strict-Transport-Security': {'expected': None, 'weight': 3},
        'Content-Security-Policy': {'expected': None, 'weight': 3},
        'Referrer-Policy': {'expected': None, 'weight': 1},
        'Permissions-Policy': {'expected': None, 'weight': 1},
        'X-Frame-Options': {'expected': ['DENY', 'SAMEORIGIN'], 'weight': 2}
    }

    try:
        # Make request with proper error handling
        response = requests.get(website, headers=headers, timeout=15)
        response.raise_for_status()

        # Analyze security headers
        total_score = 0
        max_score = sum(header_info['weight'] for header_info in security_headers.values())
        issues = []

        for header, config in security_headers.items():
            header_value = response.headers.get(header)
            expected = config['expected']
            weight = config['weight']
            
            if header_value:
                if expected is None:
                    # Header present, that's good enough
                    total_score += weight
                    logger.debug(f"Security header {header} present: {header_value}")
                elif isinstance(expected, list):
                    # Check if value is in expected list
                    if any(exp in header_value for exp in expected):
                        total_score += weight
                    else:
                        issues.append(f"{header} has unexpected value: {header_value}")
                        total_score += weight * 0.5  # Partial credit
                elif expected.lower() in header_value.lower():
                    total_score += weight
                else:
                    issues.append(f"{header} has non-ideal value: {header_value} (expected: {expected})")
                    total_score += weight * 0.5  # Partial credit
            else:
                issues.append(f"Missing security header: {header}")

        # Check for information disclosure headers
        revealing_headers = {
            'Server', 'X-Powered-By', 'X-AspNet-Version', 'X-Generator'
        }
        found_revealing = revealing_headers.intersection(response.headers.keys())
        
        if found_revealing:
            issues.append(f"Information disclosure headers found: {', '.join(found_revealing)}")
            total_score -= 1  # Penalty for revealing headers

        # Calculate security score percentage
        security_score = max(0, total_score / max_score)
        
        logger.info(f"Security headers analysis for {website}: {security_score:.2f} score ({total_score}/{max_score})")
        
        if issues:
            logger.warning(f"Security issues found: {issues}")

        # Determine result based on security score
        if security_score >= 0.9:
            return "🟢"
        elif security_score >= 0.6:
            return "🟠"
        else:
            return "🔴"

    except (Timeout, HTTPError) as e:
        logger.warning(f"HTTP/Timeout error for {website}: {e}")
        return "⚪"
    except RequestException as e:
        logger.warning(f"Request error for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error for {website}: {e}")
        return "⚪"
