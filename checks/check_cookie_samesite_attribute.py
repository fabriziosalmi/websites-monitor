import requests

def check_cookie_samesite_attribute(website):
    """
    Verify the SameSite attribute of cookies for the website.
    
    Args:
    - website (str): URL of the website to be checked.
    
    Returns:
    - str: "🟢" if the SameSite attribute is set correctly,
           "🔴" if SameSite attribute is missing or set to None without Secure,
           "🟠" if SameSite attribute is set to None but with Secure,
           "⚪" for any errors.
    """

    try:
        response = requests.get(website)
        cookies = response.cookies

        # If there are no cookies, return green as it's not applicable
        if not cookies:
            return "🟢"
        
        for cookie in cookies:
            samesite_attr = cookie.get("SameSite")

            if not samesite_attr:
                print(f"Cookie {cookie.name} does not have SameSite attribute.")
                return "🔴"
            elif samesite_attr == "None" and not cookie.get("Secure"):
                print(f"Cookie {cookie.name} has SameSite=None without Secure.")
                return "🔴"
            elif samesite_attr == "None" and cookie.get("Secure"):
                print(f"Cookie {cookie.name} has SameSite=None but with Secure.")
                return "🟠"

        # If all cookies have SameSite and are either Strict or Lax
        return "🟢"

    except Exception as e:
        print(f"Error occurred: {e}")
        return "⚪"
