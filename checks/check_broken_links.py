import requests
from requests.exceptions import RequestException, Timeout, HTTPError
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def check_broken_links(website):
    """
    Check for broken links on the provided website.

    Args:
        website (str): The URL of the website to be checked.

    Returns:
        str: 
            - "🟢" if no broken links are found
            - "🟠" if some broken links are found
            - "🔴" if all links are broken
            - "⚪" if an error occurs
    """
    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        'User-Agent': 'BrokenLinkChecker/1.0'
    }

    checked_links = set()  # To avoid checking the same URL twice
    broken_link_count = 0
    total_links = 0
    max_links_to_check = 20  # Limit to avoid excessive requests

    try:
        # Method 1: Direct HTML content analysis using BeautifulSoup
        response = requests.get(website, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')

        # Find all anchor tags with href attributes
        links = soup.find_all('a', href=True)

        for link in links[:max_links_to_check]:  # Limit number of links to check
            href = link.get('href')
            
            # Skip anchor links, JavaScript calls, and mailto links
            if href.startswith(('#', 'javascript:', 'mailto:')):
                continue

            # Convert relative URLs to absolute URLs
            full_url = urljoin(website, href)

            # Skip already checked links
            if full_url in checked_links:
                continue

            checked_links.add(full_url)

            try:
                # Check the status of the link
                link_response = requests.get(full_url, headers=headers, allow_redirects=True, timeout=5)
                if 400 <= link_response.status_code < 600:
                    print(f"Broken link found: {full_url} (Status: {link_response.status_code})")
                    broken_link_count += 1

            except (Timeout, HTTPError, RequestException) as e:
                print(f"Error while checking link: {full_url}: {e}")
                broken_link_count += 1

            total_links += 1

        # Determine the result based on the broken link analysis
        if total_links == 0:
            print("No valid links found on the website.")
            return "⚪"
        elif broken_link_count == 0:
            return "🟢"
        elif broken_link_count < total_links:
            return "🟠"
        else:
            return "🔴"

    except (Timeout, HTTPError, RequestException) as e:
        print(f"Request error occurred while checking broken links for {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking broken links for {website}: {e}")
        return "⚪"
