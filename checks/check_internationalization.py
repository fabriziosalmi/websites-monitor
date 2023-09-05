from bs4 import BeautifulSoup

def check_internationalization(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    lang_tags = soup.find_all(attrs={"lang": True})
    if len(lang_tags) > 1:
        return "🟢"
    return "🔴"
