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

        # Check each recommended header for presence and correct value.
        for header, ideal_value in recommended_headers.items():
            value = headers.get(header)
            if value:
                headers_found += 1
                if ideal_value and value != ideal_value:
                    headers_partially_implemented += 1

        # Check for revealing headers which might disclose sensitive information.
        revealing_headers = set(['Server', 'X-Powered-By', 'X-AspNet-Version'])
        if revealing_headers.intersection(headers):
            headers_partially_implemented += 1
        
        # Decision-making based on the checks.
        if headers_found == len(recommended_headers):
            if headers_partially_implemented == 0:
                return "🟢"  # Green: All headers properly implemented
            else:
                return "🟠"  # Orange: Headers are present but not all are ideally implemented
        else:
            return "🔴"  # Red: Some headers are missing

    except requests.RequestException:
        print(f"Network-related error occurred while checking security headers for {website}.")
        return "🔴"  # Red: Error occurred

    except Exception as e:
        print(f"An unexpected error occurred while checking security headers for {website}: {e}")
        return "🔴"  # Red: Error occurred
