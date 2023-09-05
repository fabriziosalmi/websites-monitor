import requests
from bs4 import BeautifulSoup

def check_broken_links(website):
    try:
        response = requests.get(f"https://{website}")
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')
        
        for link in links:
            url = link.get('href')
            if url.startswith('/'):
                url = f"https://{website}{url}"
            link_response = requests.get(url)
            if link_response.status_code == 404:
                return "🔴"
        return "🟢"
    except Exception as e:
        print(f"An error occurred while checking broken links for {website}: {e}")
        return "🔴"
