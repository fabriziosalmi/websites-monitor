from bs4 import BeautifulSoup
import requests

def check_open_graph_protocol(website):
    response = requests.get(f"https://{website}")
    soup = BeautifulSoup(response.content, 'html.parser')
    meta_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
    
    if meta_tags:
        return "🟢"
    else:
        return "🔴"
