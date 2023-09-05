from bs4 import BeautifulSoup
import requests

def check_clientside_rendering(website):
    response = requests.get(f"https://{website}")
    soup = BeautifulSoup(response.content, 'html.parser')
    scripts = soup.find_all('script')
    
    if len(scripts) > 10:
        return "🔴"
    else:
        return "🟢"
