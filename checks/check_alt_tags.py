import requests
from bs4 import BeautifulSoup

def check_alt_tags(website):
    try:
        response = requests.get(f"https://{website}")
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all('img')
        
        for img in images:
            if not img.get('alt'):
                return "🔴"
        return "🟢"
    except Exception as e:
        print(f"An error occurred while checking alt tags for {website}: {e}")
        return "🔴"
