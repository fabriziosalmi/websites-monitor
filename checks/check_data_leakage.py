import requests
import logging
from requests.exceptions import RequestException, HTTPError
from urllib.parse import urlparse
import re
import time

logger = logging.getLogger(__name__)

# Rate limiting cache for GitHub API
_github_rate_limit = {
    'last_request': 0,
    'min_interval': 1.0  # Respect GitHub API rate limits
}

def check_data_leakage(website: str, token: str) -> str:
    """
    Check public repositories on GitHub for potential data leakages related to the website.

    Args:
        website (str): URL of the website to be checked.
        token (str): GitHub Personal Access Token for authenticated requests.

    Returns:
        str:
            - "🟢" if no potential data leakages are found.
            - "🟡" if minor/low-risk leakages are found.
            - "🔴" if critical data leakages are identified.
            - "⚪" if any errors occurred.
    """
    # Input validation and normalization
    if not website or not token:
        logger.error("Website URL and GitHub token are required")
        return "⚪"
    
    # Normalize domain
    website = website.lower().strip()
    website = re.sub(r'^https?://', '', website)
    website = re.sub(r'^www\.', '', website)
    website = website.split('/')[0]
    
    # Validate domain format
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]$', website):
        logger.error(f"Invalid domain format: {website}")
        return "⚪"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "WebsiteMonitor/1.0"
    }

    # Enhanced detection patterns with risk categorization
    search_patterns = {
        # Critical risks
        "critical": [
            f"{website} api_key",
            f"{website} secret_key", 
            f"{website} private_key",
            f"{website} database_password",
            f"{website} db_pass",
            f"{website} auth_token"
        ],
        # High risks  
        "high": [
            f"{website} password",
            f"{website} credentials",
            f"{website} access_token",
            f"{website} session_secret"
        ],
        # Medium risks
        "medium": [
            f"{website} config",
            f"{website} env",
            f"{website} .env",
            f"{website} database_url"
        ],
        # Low risks
        "low": [
            f"{website} email",
            f"{website} username",
            f"{website} host"
        ]
    }

    # Performance optimization - rate limiting
    current_time = time.time()
    time_since_last = current_time - _github_rate_limit['last_request']
    if time_since_last < _github_rate_limit['min_interval']:
        time.sleep(_github_rate_limit['min_interval'] - time_since_last)

    try:
        findings = {"critical": [], "high": [], "medium": [], "low": []}
        
        for risk_level, patterns in search_patterns.items():
            for pattern in patterns:
                _github_rate_limit['last_request'] = time.time()
                
                # Enhanced search query
                query = f'"{pattern}" in:code'
                url = f"https://api.github.com/search/code?q={query}&sort=indexed&order=desc"
                
                response = requests.get(url, headers=headers, timeout=15)
                
                # Handle rate limiting
                if response.status_code == 403:
                    reset_time = response.headers.get('X-RateLimit-Reset')
                    if reset_time:
                        logger.warning(f"GitHub API rate limit hit, reset at {reset_time}")
                    break
                
                response.raise_for_status()
                json_data = response.json()
                
                if json_data.get("total_count", 0) > 0:
                    items = json_data.get("items", [])[:3]  # Limit to first 3 results
                    for item in items:
                        findings[risk_level].append({
                            "pattern": pattern,
                            "repository": item.get("repository", {}).get("full_name", "unknown"),
                            "file": item.get("name", "unknown"),
                            "url": item.get("html_url", "")
                        })
                
                # Small delay between requests
                time.sleep(0.5)
        
        # Improved scoring and categorization
        total_critical = len(findings["critical"])
        total_high = len(findings["high"]) 
        total_medium = len(findings["medium"])
        total_low = len(findings["low"])
        
        # Log findings
        for risk_level, items in findings.items():
            for finding in items[:2]:  # Log first 2 findings per risk level
                logger.warning(f"Data leakage ({risk_level}): {finding['pattern']} in {finding['repository']}/{finding['file']}")
        
        # Categorization logic
        if total_critical > 0:
            logger.critical(f"Critical data leakage found for {website}: {total_critical} instances")
            return "🔴"
        elif total_high >= 2 or (total_high >= 1 and total_medium >= 2):
            logger.error(f"High-risk data leakage found for {website}")
            return "🔴"
        elif total_high >= 1 or total_medium >= 3:
            logger.warning(f"Medium-risk data leakage found for {website}")
            return "🟡"
        elif total_medium >= 1 or total_low >= 5:
            logger.info(f"Low-risk data leakage found for {website}")
            return "🟡"
        else:
            logger.info(f"No significant data leakages found for {website}")
            return "🟢"

    except HTTPError as e:
        if e.response.status_code == 403:
            logger.error(f"GitHub API access forbidden for {website} - check token permissions")
        elif e.response.status_code == 422:
            logger.error(f"Invalid search query for {website}")
        else:
            logger.error(f"HTTP error {e.response.status_code} while checking data leakage for {website}: {e}")
        return "⚪"
    except RequestException as e:
        logger.error(f"Request error while checking data leakage for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error while checking data leakage for {website}: {e}")
        return "⚪"
