from bs4 import BeautifulSoup

def check_semantic_markup(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    json_ld = soup.find_all(type="application/ld+json")
    microdata = soup.find_all(attrs={"itemscope": True})
    if json_ld or microdata:
        return "🟢"
    return "🔴"
