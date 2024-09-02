import requests
from requests.exceptions import RequestException, Timeout, HTTPError

def check_cookie_samesite_attribute(website: str) -> str:
    """
    Verify the SameSite attribute of cookies for the website.

    Args:
        website (str): URL of the website to be checked.

    Returns:
        str:
            - "🟢" if the SameSite attribute is set correctly
            - "🔴" if SameSite attribute is missing or set to None without Secure
            - "🟠" if SameSite attribute is set to None but with Secure
            - "⚪" for any errors
    """
    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        'User-Agent': 'SameSiteCookieChecker/1.0'
    }

    try:
        # Make a request to the website
        response = requests.get(website, headers=headers, timeout=10)
        response.raise_for_status()

        # Retrieve the cookies from the response
        cookies = response.cookies

        # If there are no cookies, return "🟢" as the check is not applicable
        if not cookies:
            print(f"No cookies found for {website}.")
            return "🟢"
        
        for cookie in cookies:
            samesite_attr = cookie.get("samesite")

            if samesite_attr is None:
                print(f"Cookie '{cookie.name}' does not have the SameSite attribute set.")
                return "🔴"
            elif samesite_attr.lower() == "none" and not cookie.get("secure"):
                print(f"Cookie '{cookie.name}' has SameSite set to None without the Secure attribute.")
                return "🔴"
            elif samesite_attr.lower() == "none" and cookie.get("secure"):
                print(f"Cookie '{cookie.name}' has SameSite set to None but with the Secure attribute.")
                return "🟠"
            elif samesite_attr.lower() in ["strict", "lax"]:
                continue
            else:
                print(f"Cookie '{cookie.name}' has an unexpected SameSite value: {samesite_attr}")
                return "🔴"

        # If all cookies pass the checks
        print(f"All cookies for {website} have a correct SameSite attribute set.")
        return "🟢"

    except (Timeout, HTTPError) as e:
        print(f"Timeout or HTTP error occurred while checking SameSite attribute for {website}: {e}")
        return "⚪"
    except RequestException as e:
        print(f"Request-related error occurred while checking SameSite attribute for {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking SameSite attribute for {website}: {e}")
        return "⚪"
