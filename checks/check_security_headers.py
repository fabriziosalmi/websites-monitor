import requests
from requests.exceptions import RequestException, Timeout, HTTPError

def check_security_headers(website: str) -> str:
    """
    Check for the presence and correct implementation of recommended security headers on a website.

    Args:
        website (str): URL of the website to be checked.

    Returns:
        str:
            - "🟢" if all recommended headers are properly implemented.
            - "🟠" if headers are present but not all are ideally implemented.
            - "🔴" if some recommended headers are missing.
            - "⚪" for any errors.
    """
    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        'User-Agent': 'SecurityHeaderChecker/1.0'
    }

    # Recommended security headers and their expected values
    recommended_headers = {
        'X-Content-Type-Options': "nosniff",
        'X-XSS-Protection': "1; mode=block",
        'Strict-Transport-Security': None,  # Expected to be present, value not strictly defined here
        'Content-Security-Policy': None,    # Expected to be present, value depends on the site's policy
        'Referrer-Policy': None,            # Expected to be present, value depends on the site's policy
        'Permissions-Policy': None          # Expected to be present, value depends on the site's policy
    }

    try:
        # Make a request to the website
        response = requests.get(website, headers=headers, timeout=10)
        response.raise_for_status()

        # Retrieve headers from the response
        headers_found = 0
        headers_partially_implemented = 0

        # Check each recommended header for presence and correct value
        for header, ideal_value in recommended_headers.items():
            value = response.headers.get(header)
            if value:
                headers_found += 1
                if ideal_value and value != ideal_value:
                    print(f"Header '{header}' is present but has a non-ideal value: {value}")
                    headers_partially_implemented += 1
            else:
                print(f"Missing recommended security header: {header}")

        # Check for revealing headers that might disclose sensitive information
        revealing_headers = {'Server', 'X-Powered-By', 'X-AspNet-Version'}
        revealing_present = revealing_headers.intersection(response.headers)

        if revealing_present:
            headers_partially_implemented += 1
            print(f"Revealing headers present: {', '.join(revealing_present)}")

        # Determine the result based on the header checks
        if headers_found == len(recommended_headers):
            if headers_partially_implemented == 0:
                print(f"All recommended security headers are properly implemented for {website}.")
                return "🟢"
            else:
                print(f"Some headers are not ideally implemented for {website}.")
                return "🟠"
        else:
            print(f"Some recommended headers are missing for {website}.")
            return "🔴"

    except (Timeout, HTTPError) as e:
        print(f"Timeout or HTTP error occurred while checking security headers for {website}: {e}")
        return "⚪"
    except RequestException as e:
        print(f"Request-related error occurred while checking security headers for {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking security headers for {website}: {e}")
        return "⚪"
