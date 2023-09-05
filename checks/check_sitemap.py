import requests

def check_sitemap(website):
    try:
        response = requests.get(f"https://{website}/sitemap.xml")
        if response.status_code == 200:
            return "🟢"
        else:
            return "🔴"
    except Exception:
        return "🔴"
