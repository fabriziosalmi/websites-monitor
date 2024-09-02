import requests
from requests.exceptions import RequestException, Timeout, HTTPError

def check_subdomain_enumeration(website: str) -> (str, list):
    """
    Check for the existence of common subdomains for a given website.

    Args:
        website (str): The main domain of the website to be checked.

    Returns:
        tuple: A status symbol and a list of discovered subdomains.
            - "🟢" if no subdomains were discovered.
            - "🔴" if any subdomains were found.
            - "⚪" for unexpected errors.
    """
    # List of common subdomains to check
    SUBDOMAINS = ["www", "api", "dev", "test", "staging", "mail", "blog", "shop"]
    discovered_subdomains = []

    headers = {
        'User-Agent': 'SubdomainEnumerator/1.0'
    }

    with requests.Session() as session:
        for sub in SUBDOMAINS:
            subdomain_url = f"https://{sub}.{website}"
            try:
                # Check if the subdomain is accessible
                response = session.get(subdomain_url, headers=headers, timeout=5)
                if response.status_code == 200:
                    print(f"Discovered subdomain: {subdomain_url}")
                    discovered_subdomains.append(subdomain_url)
            except (Timeout, HTTPError) as e:
                print(f"Timeout or HTTP error occurred while checking subdomain {subdomain_url}: {e}")
                continue
            except RequestException as e:
                print(f"Request-related error occurred while checking subdomain {subdomain_url}: {e}")
                continue
            except Exception as e:
                print(f"An unexpected error occurred while checking subdomain {subdomain_url}: {e}")
                return "⚪", []

    # Determine the result based on discovered subdomains
    if discovered_subdomains:
        return "🔴", discovered_subdomains
    else:
        print(f"No subdomains discovered for {website}.")
        return "🟢", []
