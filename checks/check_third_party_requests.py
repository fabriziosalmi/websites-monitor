import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, Timeout, HTTPError

def check_third_party_requests(website: str) -> str:
    """
    Monitor the number of third-party requests made by a website.

    Args:
        website (str): URL of the website to be checked.
    
    Returns:
        str: 
            - "🔴" if the website makes a high number of third-party requests.
            - "🟢" if the number of third-party requests is acceptable.
            - "⚪" for any errors.
    """
    headers = {
        'User-Agent': 'ThirdPartyRequestChecker/1.0'
    }

    try:
        # Send an HTTP GET request to the website
        response = requests.get(website, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse the main domain from the website URL
        parsed_url = urlparse(website)
        main_domain = parsed_url.netloc

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Initialize the count for third-party requests
        third_party_requests = 0

        # Find all tags that may contain external resources
        for tag in soup.find_all(['link', 'script', 'img']):
            href = tag.get('href') or tag.get('src')
            if href:
                parsed_href = urlparse(href)
                # Count as third-party if the netloc is present and differs from the main domain
                if parsed_href.netloc and parsed_href.netloc != main_domain:
                    print(f"Third-party request detected: {href}")
                    third_party_requests += 1

        # Define what constitutes a "high" number of third-party requests (threshold can be adjusted)
        if third_party_requests > 50:
            print(f"High number of third-party requests detected ({third_party_requests}) for {website}.")
            return "🔴"
        else:
            print(f"Acceptable number of third-party requests ({third_party_requests}) for {website}.")
            return "🟢"

    except (Timeout, HTTPError) as e:
        print(f"Timeout or HTTP error occurred while checking third-party requests for {website}: {e}")
        return "⚪"
    except RequestException as e:
        print(f"Request-related error occurred while checking third-party requests for {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking third-party requests for {website}: {e}")
        return "⚪"
