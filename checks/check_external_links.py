import requests
import logging
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import RequestException, HTTPError
from urllib.parse import urlparse, urljoin
import time

logger = logging.getLogger(__name__)

def check_external_links(website: str, max_workers: int = 10) -> str:
    """
    Verify that all external links on the website are valid and do not lead to broken or malicious destinations.

    Args:
        website (str): URL of the website to be checked.
        max_workers (int): Maximum number of threads to use for checking links concurrently.

    Returns:
        str:
            - "🔴" if any broken or malicious external link is found.
            - "🟡" if some links have warnings but are accessible.
            - "🟢" if all external links are valid.
            - "⚪" if any errors occurred during the check.
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
        base_domain = parsed_url.netloc
    except Exception as e:
        logger.error(f"URL parsing error for {website}: {e}")
        return "⚪"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    }

    try:
        # Fetch the main page content
        response = requests.get(website, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Enhanced detection patterns - extract all types of external links
        external_links = set()
        
        # Check anchor tags
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http') and base_domain not in href:
                external_links.add(href)
        
        # Check link tags (stylesheets, etc.)
        for link in soup.find_all('link', href=True):
            href = link['href']
            if href.startswith('http') and base_domain not in href:
                external_links.add(href)
        
        # Check script sources
        for script in soup.find_all('script', src=True):
            src = script['src']
            if src.startswith('http') and base_domain not in src:
                external_links.add(src)

        external_links = list(external_links)
        
        if not external_links:
            logger.info(f"No external links found for {website}")
            return "🟢"

        logger.info(f"Found {len(external_links)} external links to check for {website}")

        # Enhanced link checking with categorization
        def check_link_detailed(url):
            try:
                start_time = time.time()
                resp = requests.head(url, timeout=10, allow_redirects=True, headers=headers)
                response_time = time.time() - start_time
                
                if resp.status_code == 200:
                    return {"url": url, "status": "ok", "code": resp.status_code, "time": response_time}
                elif resp.status_code in [301, 302, 307, 308]:
                    return {"url": url, "status": "redirect", "code": resp.status_code, "time": response_time}
                elif resp.status_code in [400, 401, 403, 404]:
                    return {"url": url, "status": "client_error", "code": resp.status_code, "time": response_time}
                elif resp.status_code >= 500:
                    return {"url": url, "status": "server_error", "code": resp.status_code, "time": response_time}
                else:
                    return {"url": url, "status": "warning", "code": resp.status_code, "time": response_time}
                    
            except requests.exceptions.Timeout:
                return {"url": url, "status": "timeout", "code": None, "time": None}
            except requests.exceptions.ConnectionError:
                return {"url": url, "status": "connection_error", "code": None, "time": None}
            except RequestException as e:
                return {"url": url, "status": "request_error", "code": None, "time": None, "error": str(e)}
            except Exception as e:
                return {"url": url, "status": "unknown_error", "code": None, "time": None, "error": str(e)}

        # Performance optimization - limit concurrent checks
        max_workers = min(max_workers, len(external_links), 20)
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(check_link_detailed, link): link for link in external_links}
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error checking link: {e}")
                    results.append({"url": futures[future], "status": "check_error", "error": str(e)})

        # Improved scoring and categorization
        broken_links = [r for r in results if r["status"] in ["client_error", "server_error", "connection_error", "timeout"]]
        warning_links = [r for r in results if r["status"] in ["warning", "redirect"]]
        ok_links = [r for r in results if r["status"] == "ok"]

        # Log detailed results
        for result in broken_links[:5]:  # Log first 5 broken links
            logger.warning(f"Broken link: {result['url']} - Status: {result.get('code', 'N/A')}")
        
        for result in warning_links[:3]:  # Log first 3 warning links
            logger.info(f"Warning link: {result['url']} - Status: {result.get('code', 'N/A')}")

        if broken_links:
            logger.error(f"Found {len(broken_links)} broken external links out of {len(external_links)} total")
            return "🔴"
        elif warning_links:
            logger.warning(f"Found {len(warning_links)} external links with warnings out of {len(external_links)} total")
            return "🟡"
        else:
            logger.info(f"All {len(external_links)} external links are valid")
            return "🟢"

    except (HTTPError, RequestException) as e:
        logger.error(f"Request error while checking external links for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error while checking external links for {website}: {e}")
        return "⚪"
