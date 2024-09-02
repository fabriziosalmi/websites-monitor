import requests
from requests.exceptions import RequestException, Timeout, HTTPError

def check_domainsblacklists_blacklist(domain):
    """
    Check if a domain is present in a large blacklist file hosted online.

    Args:
        domain (str): The domain to check against the blacklist.

    Returns:
        str: 
            - "🔴" if the domain is found in the blacklist
            - "🟢" if the domain is not found in the blacklist
            - "⚪" if an error occurs
    """
    url = "https://github.com/fabriziosalmi/blacklists/releases/download/latest/blacklist.txt"
    
    headers = {
        'User-Agent': 'DomainBlacklistChecker/1.0'
    }

    try:
        # Stream the response to handle large files efficiently
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()

        # Read and process the file line by line to avoid loading it into memory
        for line in response.iter_lines(decode_unicode=True):
            if line and line.strip() == domain:
                print(f"Domain {domain} found in blacklist.")
                return "🔴"

        print(f"Domain {domain} not found in blacklist.")
        return "🟢"

    except (Timeout, HTTPError) as e:
        print(f"Timeout or HTTP error occurred while checking domain {domain} against the blacklist: {e}")
        return "⚪"
    except RequestException as e:
        print(f"Request-related error occurred while checking domain {domain} against the blacklist: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking domain {domain} against the blacklist: {e}")
        return "⚪"
