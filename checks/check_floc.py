import requests

def check_floc(website):
    response = requests.get(f"https://{website}")
    if 'Permissions-Policy: interest-cohort=()' in response.headers.get('Permissions-Policy', ''):
        return "🟢"
    else:
        return "🔴"
