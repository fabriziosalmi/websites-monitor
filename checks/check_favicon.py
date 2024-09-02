import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, HTTPError

def check_favicon(website: str) -> str:
    """
    Check if the website has a valid favicon.

    Args:
        website (str): URL of the website to be checked.

    Returns:
        str: 
            - "🟢" if a valid favicon is found.
            - "🔴" if no valid favicon is found.
            - "⚪" if an error occurred during the check.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    }

    try:
        # Check the default location for favicon.ico
        default_favicon_url = f"https://{website}/favicon.ico"
        response = requests.get(default_favicon_url, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"Favicon found at default location: {default_favicon_url}")
            return "🟢"

        # Check the HTML for a <link> tag with a favicon reference
        response = requests.get(f"https://{website}", headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for favicon in <link> tags
        icon_link = soup.find('link', rel=lambda x: x in ['icon', 'shortcut icon'] if x else False)
        if icon_link and icon_link.get('href'):
            favicon_url = icon_link['href']

            # Handle relative URL
            if favicon_url.startswith('//'):
                favicon_url = f"https:{favicon_url}"
            elif not favicon_url.startswith(('http://', 'https://')):
                favicon_url = f"https://{website}/{favicon_url.lstrip('/')}"

            # Check the validity of the found favicon URL
            response = requests.get(favicon_url, headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"Favicon found at {favicon_url}")
                return "🟢"

        print(f"No valid favicon found for {website}.")
        return "🔴"
        
    except (HTTPError, RequestException) as e:
        print(f"HTTP or request error occurred while checking favicon for {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking favicon for {website}: {e}")
        return "⚪"
