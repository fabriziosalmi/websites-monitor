import requests

def check_floc(website):
    """
    Check if the website has opted out of FLoC (Federated Learning of Cohorts).
    
    Args:
    - website (str): URL of the website to be checked.
    
    Returns:
    - str: "🟢" if the site has opted out of FLoC, "🔴" otherwise.
    """
    try:
        response = requests.get(f"https://{website}")
        permissions_policy = response.headers.get('Permissions-Policy', '').lower()
        
        if 'interest-cohort=()' in permissions_policy:
            return "🟢"
        else:
            return "🔴"
            
    except requests.RequestException as e:
        print(f"An error occurred while checking FLoC for {website}: {e}")
        return "🔴"
