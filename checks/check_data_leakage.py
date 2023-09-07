import requests

def check_data_leakage(website, token):
    """
    Check public repositories for potential data leakages related to the website.
    
    Args:
    - website (str): URL of the website to be checked.
    - token (str): GitHub Personal Access Token for authenticated requests.
    
    Returns:
    - str: "🟢" if no potential data leakages are found,
           "🔴" if potential data leakages are identified,
           "⚪" if any errors occurred.
    """
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    search_keywords = ["api key", "secret", "password", "db_credentials", "database_url", "auth_token"]
    
    try:
        for keyword in search_keywords:
            query = f"{keyword} in:code {website}"
            response = requests.get(f"https://api.github.com/search/code?q={query}", headers=headers)
            response.raise_for_status()
            
            json_data = response.json()
            if json_data["total_count"] > 0:
                # Potential data leakage found
                return "🔴"
        
        # No potential data leakages identified
        return "🟢"

    except Exception as e:
        print(f"Error occurred: {e}")
        return "⚪"

# Example usage (ensure to replace 'YOUR_GITHUB_TOKEN' with your actual token)
# print(check_data_leakage("example.com", "YOUR_GITHUB_TOKEN"))
