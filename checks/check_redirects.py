import requests
from requests.exceptions import RequestException, Timeout, HTTPError

def check_redirects(website: str) -> str:
    """
    Verify if a website using HTTP redirects to its HTTPS counterpart.

    Args:
        website (str): The URL (without protocol) of the website to check.

    Returns:
        str:
            - "🟢" if the site redirects from HTTP to HTTPS.
            - "🔴" if it does not redirect from HTTP to HTTPS.
            - "⚪" in case of an error.
    """
    headers = {
        "User-Agent": "HTTPtoHTTPSRedirectChecker/1.0"
    }

    try:
        # Make an HTTP request to the site and prevent automatic redirects
        response = requests.get(f"http://{website}", headers=headers, allow_redirects=False)
        redirect_location = response.headers.get('Location', '')

        # Check if the response indicates a redirect to the HTTPS version of the site
        if response.status_code in [301, 302, 303, 307, 308] and redirect_location.startswith(f"https://{website}"):
            print(f"Website {website} redirects from HTTP to HTTPS.")
            return "🟢"
        else:
            print(f"Website {website} does not redirect from HTTP to HTTPS.")
            return "🔴"

    except (Timeout, HTTPError) as e:
        print(f"Timeout or HTTP error occurred while checking redirects for {website}: {e}")
        return "⚪"
    except RequestException as e:
        print(f"Request-related error occurred while checking redirects for {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking redirects for {website}: {e}")
        return "⚪"
