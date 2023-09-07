import requests
from bs4 import BeautifulSoup

def check_cookie_policy(website):
    """
    Verify if the website has a cookie policy and it's accessible to users.
    
    Args:
    - website (str): URL of the website to be checked.
    
    Returns:
    - str: "🔴" if no cookie policy is found or if it's inaccessible, "🟢" if a cookie policy is found and accessible, "🟠" for any errors.
    """
    try:
        response = requests.get(website)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Common keywords associated with cookie policies
        keywords = ["cookie policy", "cookie statement", "use of cookies"]

        # Check if any of the keywords are present in the page's text
        page_text = soup.get_text().lower()
        if any(keyword in page_text for keyword in keywords):
            return "🟢"  # Cookie policy found
        return "🔴"  # No cookie policy found
    except Exception as e:
        print(f"Error checking cookie policy for {website}. Error: {e}")
        return "🟠"  # Error occurred
