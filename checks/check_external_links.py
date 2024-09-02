import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import RequestException, HTTPError

def check_external_links(website: str, max_workers: int = 10) -> str:
    """
    Verify that all external links on the website are valid and do not lead to broken or malicious destinations.

    Args:
        website (str): URL of the website to be checked.
        max_workers (int): Maximum number of threads to use for checking links concurrently.

    Returns:
        str:
            - "🔴" if any broken or malicious external link is found.
            - "🟢" if all external links are valid.
            - "⚪" if any errors occurred during the check.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    }

    try:
        # Fetch the main page content
        response = requests.get(website, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract external links
        external_links = [
            link['href'] for link in soup.find_all('a', href=True)
            if link['href'].startswith('http') and not link['href'].startswith(website)
        ]

        if not external_links:
            print(f"No external links found for {website}.")
            return "🟢"

        # Helper function to check link validity
        def is_link_broken(url):
            try:
                resp = requests.get(url, timeout=5)
                if resp.status_code != 200:
                    print(f"Broken link found: {url} (Status code: {resp.status_code})")
                    return True
                return False
            except RequestException as e:
                print(f"Error checking link: {url}. Exception: {e}")
                return True

        # Use ThreadPoolExecutor to concurrently check links
        broken_links_found = False
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all the link checks to the executor
            futures = {executor.submit(is_link_broken, link): link for link in external_links}
            
            # Process results as they are completed
            for future in as_completed(futures):
                if future.result():  # If any link is broken
                    broken_links_found = True

        if broken_links_found:
            return "🔴"  # Broken external links found
        return "🟢"  # All external links are valid

    except (HTTPError, RequestException) as e:
        print(f"HTTP or request error occurred while checking external links for {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking external links for {website}: {e}")
        return "⚪"
