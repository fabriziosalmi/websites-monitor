from bs4 import BeautifulSoup

def check_amp_compatibility(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    amp_html = soup.find_all("html", attrs={"⚡": ""}) or soup.find_all("html", attrs={"amp": ""})
    if amp_html:
        return "🟢"
    return "🔴"
