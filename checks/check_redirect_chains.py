import requests

def check_redirect_chains(website):
    """
    Check the number of redirects that a website triggers.
    
    Args:
    - website (str): The URL of the website to check.
    
    Returns:
    - str: "🟢" if no redirects, "🟠" if there's one redirect, "🔴" if multiple redirects, 
           and "⚪" in case of an error.
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
                break  # We already know there are multiple redirects, no need to continue
            response = requests.get(response.headers['location'], headers=headers, allow_redirects=False)

        if redirect_count == 0:
            return "🟢"
        elif redirect_count == 1:
            return "🟠"
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking redirects for {website}: {e}")
        return "⚪"
