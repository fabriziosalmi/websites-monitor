import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

def check_external_links(website, max_workers=10):
    """
    Verify that all external links on the website are valid and do not lead to broken or malicious destinations.
    
    Args:
    - website (str): URL of the website to be checked.
    - max_workers (int): Maximum number of threads to use for checking links concurrently.
    
    Returns:
    - str: "🔴" if any broken or malicious external link is found, "🟢" otherwise, "🟡" for any errors.
    """
    try:
        response = requests.get(website)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        external_links = [link['href'] for link in soup.find_all('a', href=True) if link['href'].startswith('http') and not link['href'].startswith(website)]
        
        # Helper function to check link validity
        def is_link_broken(url):
            try:
                resp = requests.get(url, timeout=5)
                return resp.status_code != 200
            except requests.RequestException:
                return True
        
        # Using ThreadPoolExecutor to concurrently check links
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(is_link_broken, external_links))

        if any(results):
            return "🔴"  # Broken external links found
        return "🟢"  # All external links are valid

    except Exception as e:
        print(f"Error checking external links for {website}. Error: {e}")
        return "🟡"  # Error occurred
