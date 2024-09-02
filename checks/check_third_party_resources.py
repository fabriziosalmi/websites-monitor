import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, Timeout, HTTPError

def check_third_party_resources(website: str) -> str:
    """
    Check for third-party resources loaded by the website.

    Args:
        website (str): URL of the website to be checked.

    Returns:
        str:
            - "🟢" if the number of third-party resources is minimal.
            - "🟠" if there is a moderate number of third-party resources.
            - "🔴" if there is a high number of third-party resources.
            - "⚪" for any errors.
    """
    headers = {
        'User-Agent': 'ThirdPartyResourceChecker/1.0'
    }

    try:
        # Fetch the content of the page
        response = requests.get(website, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse the main domain from the website URL
        main_domain = urlparse(website).netloc

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Initialize the list to store third-party domains
        third_party_domains = set()

        # Find all tags that may contain external resources
        for tag in soup.find_all(['script', 'link', 'img']):
            src_or_href = tag.get('src') or tag.get('href')
            if src_or_href:
                domain = urlparse(src_or_href).netloc
                # Check if the domain is a third-party domain
                if domain and domain != main_domain:
                    third_party_domains.add(domain)
                    print(f"Third-party resource detected: {src_or_href}")

        third_party_count = len(third_party_domains)

        # Return the status based on the count of third-party resources
        if third_party_count == 0:
            print(f"No third-party resources detected for {website}.")
            return "🟢"
        elif third_party_count <= 5:
            print(f"Moderate number of third-party resources ({third_party_count}) detected for {website}.")
            return "🟠"
        else:
            print(f"High number of third-party resources ({third_party_count}) detected for {website}.")
            return "🔴"

    except (Timeout, HTTPError) as e:
        print(f"Timeout or HTTP error occurred while checking third-party resources for {website}: {e}")
        return "⚪"
    except RequestException as e:
        print(f"Request-related error occurred while checking third-party resources for {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking third-party resources for {website}: {e}")
        return "⚪"
