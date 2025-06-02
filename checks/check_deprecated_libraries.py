import requests
import logging
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from urllib.parse import urlparse
import re

logger = logging.getLogger(__name__)

def check_deprecated_libraries(website: str) -> str:
    """
    Checks if a website is using deprecated JavaScript libraries.

    Args:
        website (str): The URL of the website to check.

    Returns:
         str:
            - "🟢" if no deprecated libraries are found.
            - "🟡" if deprecated but low-risk libraries are found.
            - "🔴" if critically deprecated libraries are found.
            - "⚪" if any errors occur during the check.
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

    try:
        response = requests.get(website, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Enhanced detection patterns - comprehensive library database
        deprecated_libraries = {
            # Critical security risks
            "jquery": {
                "versions": ["1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "2.0", "2.1"],
                "risk": "critical",
                "reason": "Multiple XSS vulnerabilities"
            },
            "angular": {
                "versions": ["1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6"],
                "risk": "critical", 
                "reason": "End of life, security vulnerabilities"
            },
            "prototype": {
                "versions": ["1."],
                "risk": "critical",
                "reason": "Unmaintained, security issues"
            },
            
            # High risks
            "modernizr": {
                "versions": ["2."],
                "risk": "high",
                "reason": "Outdated feature detection"
            },
            "dojo": {
                "versions": ["1."],
                "risk": "high", 
                "reason": "Legacy version with issues"
            },
            "mootools": {
                "versions": ["1."],
                "risk": "high",
                "reason": "Outdated framework"
            },
            
            # Medium risks
            "underscore": {
                "versions": ["1.0", "1.1", "1.2", "1.3", "1.4", "1.5"],
                "risk": "medium",
                "reason": "Replace with lodash or native methods"
            },
            "backbone": {
                "versions": ["1.0", "1.1", "1.2"],
                "risk": "medium",
                "reason": "Legacy MVC framework"
            },
            "moment": {
                "versions": ["2."],
                "risk": "medium",
                "reason": "Large bundle size, use date-fns"
            },
            
            # Low risks but still deprecated
            "swfobject": {
                "versions": ["2."],
                "risk": "low",
                "reason": "Flash is deprecated"
            },
            "yui": {
                "versions": ["2.", "3."],
                "risk": "low",
                "reason": "Yahoo discontinued support"
            }
        }
        
        # Find all script tags
        scripts = soup.find_all('script', src=True)
        inline_scripts = soup.find_all('script', src=False)
        
        found_libraries = []
        
        # Check external scripts
        for script in scripts:
            src = script.get('src', '').lower()
            
            for library, info in deprecated_libraries.items():
                if library in src:
                    # Try to extract version
                    version_match = re.search(rf'{library}[-._]?v?(\d+\.\d+(?:\.\d+)?)', src)
                    if version_match:
                        version = version_match.group(1)
                        
                        # Check if version is deprecated
                        for deprecated_version in info["versions"]:
                            if version.startswith(deprecated_version.rstrip('.')):
                                found_libraries.append({
                                    "library": library,
                                    "version": version,
                                    "risk": info["risk"],
                                    "reason": info["reason"],
                                    "source": src
                                })
                                break
                    else:
                        # Library found but version unclear - assume deprecated
                        found_libraries.append({
                            "library": library,
                            "version": "unknown",
                            "risk": info["risk"],
                            "reason": info["reason"],
                            "source": src
                        })
        
        # Check inline scripts for library references
        for script in inline_scripts:
            script_content = script.get_text().lower()
            for library, info in deprecated_libraries.items():
                if library in script_content and any(v in script_content for v in info["versions"]):
                    found_libraries.append({
                        "library": library,
                        "version": "inline",
                        "risk": info["risk"],
                        "reason": info["reason"],
                        "source": "inline script"
                    })
        
        # Improved scoring and categorization
        if not found_libraries:
            logger.info(f"No deprecated libraries found on {website}")
            return "🟢"
        
        # Categorize by risk level
        critical_libs = [lib for lib in found_libraries if lib["risk"] == "critical"]
        high_libs = [lib for lib in found_libraries if lib["risk"] == "high"]
        medium_libs = [lib for lib in found_libraries if lib["risk"] == "medium"]
        low_libs = [lib for lib in found_libraries if lib["risk"] == "low"]
        
        # Log findings
        for lib in found_libraries:
            level = logger.critical if lib["risk"] == "critical" else logger.warning
            level(f"Deprecated {lib['library']} v{lib['version']} found: {lib['reason']}")
        
        # Return appropriate status
        if critical_libs:
            logger.critical(f"Found {len(critical_libs)} critically deprecated libraries on {website}")
            return "🔴"
        elif high_libs or len(medium_libs) >= 2:
            logger.error(f"Found high-risk deprecated libraries on {website}")
            return "🔴"
        elif medium_libs or len(low_libs) >= 3:
            logger.warning(f"Found deprecated libraries with security concerns on {website}")
            return "🟡"
        else:
            logger.info(f"Found minor deprecated libraries on {website}")
            return "🟡"
    
    except RequestException as e:
        logger.error(f"Request error while checking deprecated libraries for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error while checking deprecated libraries for {website}: {e}")
        return "⚪"
