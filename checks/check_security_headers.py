import requests

def check_security_headers(website):
    # List of recommended headers and their respective ideal values or indicators
    recommended_headers = {
        'Content-Security-Policy': None, 
        'Strict-Transport-Security': None,
        'X-Content-Type-Options': "nosniff",
        'X-Frame-Options': None,
        'X-XSS-Protection': "1; mode=block",
        'Referrer-Policy': None
    }

    try:
        response = requests.get(f"https://{website}")
        headers = response.headers
        
        headers_found = 0
        headers_partially_implemented = 0

        # Check each recommended header
        for header, ideal_value in recommended_headers.items():
            value = headers.get(header)
            if value:
                headers_found += 1
                if ideal_value and value != ideal_value:
                    headers_partially_implemented += 1

        # Check for revealing headers like 'Server', 'X-Powered-By', etc.
        revealing_headers = ['Server', 'X-Powered-By', 'X-AspNet-Version']
        if any(header in headers for header in revealing_headers):
            headers_partially_implemented += 1
        
        if headers_found == len(recommended_headers) and headers_partially_implemented == 0:
            return "🟢"  # Green: All headers properly implemented
        elif headers_found > 0 and headers_partially_implemented > 0:
            return "🟠"  # Orange: Headers are present but not all are ideally implemented
        else:
            return "🔴"  # Red: Not properly implemented

    except Exception as e:
        print(f"An error occurred while checking security headers for {website}: {e}")
        return "🔴"  # Red: Error or headers not implemented
