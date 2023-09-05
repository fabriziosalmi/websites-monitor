import requests

def check_subdomain_enumeration(website):
    subdomains = ["www", "api", "dev"]
    for sub in subdomains:
        try:
            response = requests.get(f"https://{sub}.{website}")
            if response.status_code == 200:
                return "🔴"
        except Exception as e:
            continue
    return "🟢"
