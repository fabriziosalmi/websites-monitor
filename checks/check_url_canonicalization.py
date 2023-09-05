import requests
from bs4 import BeautifulSoup

def check_url_canonicalization(website):
    try:
        response = requests.get(f"https://{website}")
        soup = BeautifulSoup(response.text, 'html.parser')
        canonical_tag = soup.find('link', {'rel': 'canonical'})
        
        if canonical_tag:
            return "🟢"
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking URL canonicalization for {website}: {e}")
        return "🔴"
