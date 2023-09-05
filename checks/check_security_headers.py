import requests

def check_security_headers(website):
    result = {}
    try:
        response = requests.get(f"https://{website}")
        headers = response.headers

        # Check for Content Security Policy (CSP)
        csp = headers.get('Content-Security-Policy', None)
        if csp:
            result['CSP'] = "🟢"
        else:
            result['CSP'] = "🔴"

        # Check for revealing headers like 'Server', 'X-Powered-By', etc.
        revealing_headers = ['Server', 'X-Powered-By', 'X-AspNet-Version']
        if any(header in headers for header in revealing_headers):
            result['Revealing-Headers'] = "🔴"
        else:
            result['Revealing-Headers'] = "🟢"

    except Exception as e:
        print(f"An error occurred while checking security headers for {website}: {e}")
        result['CSP'] = "🔴"
        result['Revealing-Headers'] = "🔴"

    return result
