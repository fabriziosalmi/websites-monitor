from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException, HTTPError

def check_open_graph_protocol(website: str) -> str:
    """
    Check a given website for the presence of essential Open Graph Protocol meta tags.

    Args:
        website (str): The URL of the website to be checked.

    Returns:
        str:
            - "🟢" if essential Open Graph Protocol meta tags are found.
            - "🔴" if essential Open Graph Protocol meta tags are missing.
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

        # List of essential Open Graph tags
        essential_tags = {'og:title', 'og:type', 'og:image', 'og:url'}

        # Extract all Open Graph meta tags
        meta_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))

        # Extract the properties of found meta tags
        found_tags = {tag['property'] for tag in meta_tags if tag.has_attr('property')}

        # Check if all essential tags are present
        if essential_tags.issubset(found_tags):
            print(f"All essential Open Graph tags found for {website}.")
            return "🟢"
        else:
            print(f"Missing some essential Open Graph tags for {website}.")
            return "🔴"
    
    except (HTTPError, RequestException) as e:
        print(f"HTTP or request error occurred while checking Open Graph Protocol tags on {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking Open Graph Protocol tags on {website}: {e}")
        return "⚪"
