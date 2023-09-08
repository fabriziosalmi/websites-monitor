import requests

def check_redirects(website):
    """
    Verify if a website using HTTP redirects to its HTTPS counterpart.
    
    Args:
    - website (str): The URL (without protocol) of the website to check.
    
    Returns:
    - str: "🟢" if the site redirects from HTTP to HTTPS, "🔴" otherwise, and 
           "⚪" in case of an error.
    """
    headers = {
        "User-Agent": "HTTPtoHTTPSRedirectChecker/1.0"
    }

    try:
        response = requests.get(f"http://{website}", headers=headers, allow_redirects=False)
        redirect_location = response.headers.get('Location', '')

        if response.status_code in [301, 302, 303, 307, 308] and redirect_location.startswith(f"https://{website}"):
            return "🟢"
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking redirects for {website}: {e}")
        return "⚪"
