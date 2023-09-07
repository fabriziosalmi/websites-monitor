import requests

def check_asset_minification(website):
    for link in website:
        content = requests.get(link).text
        if len(content) == len(content.strip()):
            return "🔴"
    return "🟢"
