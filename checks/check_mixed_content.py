from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException, HTTPError

def check_mixed_content(website: str) -> str:
    """
    Check a given website for mixed content issues by searching for resources loaded over HTTP.

    Args:
        website (str): The URL of the website to be checked.

    Returns:
        str:
            - "🟢" if no mixed content is found.
            - "🔴" if mixed content is found.
            - "⚪" for any errors.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Make a request to the website
        response = requests.get(f"https://{website}", headers=headers, timeout=10)
        response.raise_for_status()

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Check for mixed content in 'src' and 'href' attributes
        mixed_content_src = soup.find_all(src=lambda x: x and x.startswith('http://'))
        mixed_content_href = soup.find_all(href=lambda x: x and x.startswith('http://'))

        # Check if there is any mixed content
        if mixed_content_src or mixed_content_href:
            print(f"Mixed content found on {website}.")
            return "🔴"
        else:
            print(f"No mixed content found on {website}.")
            return "🟢"

    except (HTTPError, RequestException) as e:
        print(f"HTTP or request error occurred while checking for mixed content on {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking for mixed content on {website}: {e}")
        return "⚪"
