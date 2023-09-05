from bs4 import BeautifulSoup

def check_subresource_integrity(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    integrity_tags = soup.find_all(attrs={"integrity": True})
    if integrity_tags:
        return "🟢"
    return "🔴"
