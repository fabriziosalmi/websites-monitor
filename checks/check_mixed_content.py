from bs4 import BeautifulSoup
import requests

def check_mixed_content(website):
    response = requests.get(f"https://{website}")
    soup = BeautifulSoup(response.content, 'html.parser')
    mixed_content = soup.find_all(src=lambda x: x and x.startswith('http:'))
    
    if mixed_content:
        return "🔴"
    else:
        return "🟢"
