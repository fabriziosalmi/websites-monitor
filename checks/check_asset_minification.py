import requests

def check_asset_minification(css_js_links):
    for link in css_js_links:
        content = requests.get(link).text
        if len(content) == len(content.strip()):
            return "🔴"
    return "🟢"
