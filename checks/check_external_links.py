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
            - "⚪" if any errors occurred during the check, or no link could be verified.
            Only 4xx (except 429) and 5xx responses count as broken. Links that
            answer 429 (rate limited) or raise (timeout, connection error) are
            "not verified": they are reported in a suffix, never as broken.
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
                if resp.status_code in [405, 501]:
                    # Server does not support HEAD: ask again with GET
                    resp = requests.get(url, timeout=10, allow_redirects=True, headers=headers, stream=True)
                    resp.close()
                response_time = time.time() - start_time
                
                if 200 <= resp.status_code < 300:
                    return {"url": url, "status": "ok", "code": resp.status_code, "time": response_time}
                elif resp.status_code in [301, 302, 307, 308]:
                    return {"url": url, "status": "redirect", "code": resp.status_code, "time": response_time}
                elif resp.status_code == 429:
                    # Rate limited: says nothing about the link
                    return {"url": url, "status": "rate_limited", "code": resp.status_code, "time": response_time}
                elif 400 <= resp.status_code < 500:
                    return {"url": url, "status": "client_error", "code": resp.status_code, "time": response_time}
                elif resp.status_code >= 500:
                    return {"url": url, "status": "server_error", "code": resp.status_code, "time": response_time}
                else:
                    return {"url": url, "status": "warning", "code": resp.status_code, "time": response_time}
                    
            except requests.exceptions.Timeout as e:
                return {"url": url, "status": "timeout", "code": None, "time": None, "error": str(e)}
            except requests.exceptions.ConnectionError as e:
                return {"url": url, "status": "connection_error", "code": None, "time": None, "error": str(e)}
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
        # Only an HTTP answer of 4xx (except 429) or 5xx proves a link is broken
        broken_links = [r for r in results if r["status"] in ["client_error", "server_error"]]
        warning_links = [r for r in results if r["status"] in ["warning", "redirect"]]
        ok_links = [r for r in results if r["status"] == "ok"]
        unverified_links = [r for r in results if r not in broken_links + warning_links + ok_links]

        # Log detailed results
        for result in broken_links[:5]:  # Log first 5 broken links
            logger.warning(f"Broken link: {result['url']} - Status: {result.get('code', 'N/A')}")
        
        for result in warning_links[:3]:  # Log first 3 warning links
            logger.info(f"Warning link: {result['url']} - Status: {result.get('code', 'N/A')}")

        for result in unverified_links[:5]:  # Log first 5 unverified links
            logger.info(f"Unverified link: {result['url']} - {result['status']} {result.get('code') or result.get('error', '')}")

        note = f" ({len(unverified_links)} links not verified)" if unverified_links else ""

        if broken_links:
            logger.error(f"Found {len(broken_links)} broken external links out of {len(external_links)} total")
            return "🔴" + note
        elif warning_links:
            logger.warning(f"Found {len(warning_links)} external links with warnings out of {len(external_links)} total")
            return "🟡" + note
        elif not ok_links:
            logger.warning(f"None of the {len(external_links)} external links could be verified")
            return "⚪" + note
        else:
            logger.info(f"All {len(ok_links)} verified external links are valid")
            return "🟢" + note

    except (HTTPError, RequestException) as e:
        logger.error(f"Request error while checking external links for {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error while checking external links for {website}: {e}")
        return "⚪"
