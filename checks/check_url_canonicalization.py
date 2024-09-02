import requests
from bs4 import BeautifulSoup
from typing import Optional
from requests.exceptions import RequestException, Timeout, HTTPError

def check_url_canonicalization(website: str) -> str:
    """
    Check if the given website uses a canonical link element to avoid potential duplicate content issues.
    
    Args:
        website (str): The URL of the website to be checked.
    
    Returns:
        str: 
            - "🟢" if a correct canonical link element is found.
            - "⚪" on some errors.
            - "🔴" otherwise.
    """
    headers = {
        'User-Agent': 'CanonicalChecker/1.0'
    }

    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    try:
        # Make a request to the website
        response = requests.get(website, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        canonical_tag = soup.find('link', {'rel': 'canonical'})

        # Check if a canonical tag is found and matches the current URL
        if canonical_tag:
            canonical_href = canonical_tag.get('href')
            if canonical_href and canonical_href.rstrip('/') == website.rstrip('/'):
                print(f"Correct canonical link element found: {canonical_href}")
                return "🟢"
            else:
                print(f"Canonical link element found but incorrect: {canonical_href}")
                return "🔴"
        else:
            print("No canonical link element found.")
            return "🔴"
    
    except (Timeout, HTTPError) as e:
        print(f"Timeout or HTTP error occurred while checking URL canonicalization for {website}: {e}")
        return "⚪"
    except RequestException as e:
        print(f"Request-related error occurred while checking URL canonicalization for {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking URL canonicalization for {website}: {e}")
        return "⚪"
