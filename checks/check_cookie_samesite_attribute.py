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

            if samesite_attr is None:
                print(f"Cookie {cookie.name} does not have the SameSite attribute set.")
                return "🔴"
            elif samesite_attr == "None" and not cookie.get("Secure"):
                print(f"Cookie {cookie.name} has SameSite set to None without the Secure attribute.")
                return "🔴"
            elif samesite_attr == "None" and cookie.get("Secure"):
                print(f"Cookie {cookie.name} has SameSite set to None but with the Secure attribute.")
                return "🟠"
            elif samesite_attr in ["Strict", "Lax"]:
                continue
            else:
                print(f"Cookie {cookie.name} has an unexpected SameSite value: {samesite_attr}")
                return "🔴"

        # If all cookies pass the checks
        return "🟢"

    except Exception as e:
        print(f"Error occurred while checking SameSite attribute for {website}. Error: {e}")
        return "⚪"
