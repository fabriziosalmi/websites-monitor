import requests
from requests.exceptions import RequestException, Timeout, HTTPError

def check_cookie_flags(website):
    """
    Check if all cookies set by the website have the Secure and HttpOnly flags.

    Args:
        website (str): URL of the website to be checked.

    Returns:
        str:
            - "🟢" if all cookies have Secure and HttpOnly flags
            - "🟠" if some cookies have Secure and HttpOnly flags, but not all
            - "🔴" if no cookies have both Secure and HttpOnly flags
            - "⚪" if an error occurs
    """
    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        'User-Agent': 'CookieFlagChecker/1.0'
    }

    try:
        response = requests.get(website, headers=headers, timeout=10)
        response.raise_for_status()

        # Fetch 'Set-Cookie' headers
        set_cookie_headers = response.headers.get('Set-Cookie', '')

        # Check if any cookies are set
        if not set_cookie_headers:
            print(f"No cookies found for {website}.")
            return "🔴"

        # Flags for checking Secure and HttpOnly
        all_secure_http_only = True
        any_secure_http_only = False

        # Iterate over each 'Set-Cookie' header
        cookies = set_cookie_headers.split(',')
        for cookie_header in cookies:
            cookie_header = cookie_header.lower()  # Case insensitive check
            if 'secure' in cookie_header and 'httponly' in cookie_header:
                any_secure_http_only = True
            else:
                all_secure_http_only = False

        # Determine the result based on the flags
        if all_secure_http_only:
            print(f"All cookies have Secure and HttpOnly flags for {website}.")
            return "🟢"
        elif any_secure_http_only:
            print(f"Some cookies have Secure and HttpOnly flags, but not all for {website}.")
            return "🟠"
        else:
            print(f"No cookies have both Secure and HttpOnly flags for {website}.")
            return "🔴"

    except (Timeout, HTTPError) as e:
        print(f"Timeout or HTTP error occurred while checking cookie flags for {website}: {e}")
        return "⚪"
    except RequestException as e:
        print(f"Request-related error occurred while checking cookie flags for {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking cookie flags for {website}: {e}")
        return "⚪"
