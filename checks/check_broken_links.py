import requests
from bs4 import BeautifulSoup

def check_broken_links(website):
    try:
        response = requests.get(f"https://{website}")
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')
        
        checked_links = set()  # To avoid checking same URL twice
        broken_link_count = 0
        total_links = 0

        for link in links:
            url = link.get('href')
            if not url or url.startswith('#') or url.startswith('javascript:'):
                continue
            if url.startswith('/'):
                url = f"https://{website}{url}"
            if url not in checked_links:
                link_response = requests.get(url, allow_redirects=True, timeout=10)
                checked_links.add(url)
                if 400 <= link_response.status_code < 600:  # Checking for client and server errors
                    broken_link_count += 1
                total_links += 1

        if broken_link_count == 0:
            return "🟢"
        elif broken_link_count < total_links:
            return "🟠"
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking broken links for {website}: {e}")
        return "⚪"
