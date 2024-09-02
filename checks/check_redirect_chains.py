import requests
from requests.exceptions import RequestException, Timeout, HTTPError

def check_redirect_chains(website: str) -> str:
    """
    Check the number of redirects that a website triggers.

    Args:
        website (str): The URL of the website to check.

    Returns:
        str: 
            - "🟢" if no redirects.
            - "🟠" if there's one redirect.
            - "🔴" if multiple redirects.
            - "⚪" in case of an error.
    """
    headers = {
        "User-Agent": "RedirectChainChecker/1.0"
    }

    try:
        redirect_count = 0
        response = requests.get(f"https://{website}", headers=headers, allow_redirects=False)

        while 'location' in response.headers:
            redirect_count += 1
            if redirect_count > 1:
                print(f"Multiple redirects detected for {website}.")
                return "🔴"
            
            # Prepare next URL to check, handling relative and absolute URLs
            next_url = response.headers['location']
            if not next_url.startswith(('http://', 'https://')):
                next_url = f"https://{website.rstrip('/')}/{next_url.lstrip('/')}"
                
            response = requests.get(next_url, headers=headers, allow_redirects=False)

        if redirect_count == 0:
            print(f"No redirects found for {website}.")
            return "🟢"
        else:
            print(f"One redirect found for {website}.")
            return "🟠"

    except (Timeout, HTTPError) as e:
        print(f"Timeout or HTTP error occurred while checking redirects for {website}: {e}")
        return "⚪"
    except RequestException as e:
        print(f"Request-related error occurred while checking redirects for {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking redirects for {website}: {e}")
        return "⚪"
