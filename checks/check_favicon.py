import requests
from bs4 import BeautifulSoup

def check_favicon(website):
    """
    Check if the website has a valid favicon.
    
    Args:
    - website (str): URL of the website to be checked.
    
    Returns:
    - str: "🟢" if a valid favicon is found, "🔴" otherwise.
    """
    try:
        # Check default favicon.ico location
        response = requests.get(f"https://{website}/favicon.ico")
        if response.status_code == 200:
            return "🟢"
        
        # If not found, check the HTML for a favicon link
        response = requests.get(f"https://{website}")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for favicon in the link tags
        icon_link = soup.find('link', rel=lambda x: x in ['icon', 'shortcut icon'] if x else False)
        if icon_link and icon_link.get('href'):
            favicon_url = icon_link['href']
            
            # Handle relative URL
            if not favicon_url.startswith(('http://', 'https://', '//')):
                favicon_url = f"https://{website}/{favicon_url.lstrip('/')}"
            
            # Check the validity of the found favicon URL
            response = requests.get(favicon_url)
            if response.status_code == 200:
                return "🟢"
            
        return "🔴"
        
    except Exception as e:
        print(f"An error occurred while checking favicon for {website}: {e}")
        return "🔴"
