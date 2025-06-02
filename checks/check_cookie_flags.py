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

        # Check if any cookies are set using the response.cookies object
        if not response.cookies:
            print(f"No cookies found for {website}.")
            return "🟢"  # No cookies means no security issue

        # Flags for checking Secure and HttpOnly
        all_secure_http_only = True
        any_secure_http_only = False
        total_cookies = len(response.cookies)

        # Check each cookie's security attributes
        for cookie in response.cookies:
            has_secure = cookie.secure
            has_httponly = hasattr(cookie, '_rest') and cookie._rest.get('HttpOnly') is not None
            
            if has_secure and has_httponly:
                any_secure_http_only = True
            else:
                all_secure_http_only = False
                print(f"Cookie '{cookie.name}' missing security flags: Secure={has_secure}, HttpOnly={has_httponly}")

        # Determine the result based on the flags
        if all_secure_http_only and total_cookies > 0:
            print(f"All cookies have Secure and HttpOnly flags for {website}.")
            return "🟢"
        elif any_secure_http_only:
            print(f"Some cookies have Secure and HttpOnly flags, but not all for {website}.")
            return "🟠"
        else:
            print(f"No cookies have both Secure and HttpOnly flags for {website}.")
            return "🔴"

    except (Timeout, HTTPError, RequestException) as e:
        print(f"Request error occurred while checking cookie flags for {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking cookie flags for {website}: {e}")
        return "⚪"
