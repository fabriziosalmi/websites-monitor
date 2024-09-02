import requests
from requests.exceptions import RequestException, HTTPError

def check_data_leakage(website: str, token: str) -> str:
    """
    Check public repositories on GitHub for potential data leakages related to the website.

    Args:
        website (str): URL of the website to be checked.
        token (str): GitHub Personal Access Token for authenticated requests.

    Returns:
        str:
            - "🟢" if no potential data leakages are found.
            - "🔴" if potential data leakages are identified.
            - "⚪" if any errors occurred.
    """
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Keywords to search for potential data leaks
    search_keywords = ["api key", "secret", "password", "db_credentials", "database_url", "auth_token"]

    try:
        for keyword in search_keywords:
            query = f"{keyword} in:code {website}"
            response = requests.get(f"https://api.github.com/search/code?q={query}", headers=headers, timeout=10)
            response.raise_for_status()
            
            json_data = response.json()
            if json_data.get("total_count", 0) > 0:
                print(f"Potential data leakage found for keyword '{keyword}' related to {website}.")
                return "🔴"
        
        print(f"No potential data leakages found for {website}.")
        return "🟢"

    except (HTTPError, RequestException) as e:
        print(f"HTTP or request error occurred while checking for data leakage: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return "⚪"
