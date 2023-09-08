import requests

def check_subdomain_enumeration(website: str) -> (str, list):
    """
    Check for the existence of common subdomains for a given website.
    
    Args:
    - website (str): The main domain of the website to be checked.
    
    Returns:
    - tuple: A status symbol and a list of discovered subdomains.
             "🟢" if no subdomains were discovered,
             "🔴" if any subdomains were found,
             "⚪" for unexpected errors.
    """
    SUBDOMAINS = ["www", "api", "dev"]
    discovered_subdomains = []
    
    with requests.Session() as session:
        for sub in SUBDOMAINS:
            try:
                response = session.get(f"https://{sub}.{website}", timeout=5)
                if response.status_code == 200:
                    discovered_subdomains.append(sub)
            except (requests.RequestException, Exception):
                continue

    if discovered_subdomains:
        return "🔴", discovered_subdomains
    return "🟢", []

# Usage:
status, subdomains_found = check_subdomain_enumeration("example.com")
print(status)
print(subdomains_found)
