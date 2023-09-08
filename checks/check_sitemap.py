import requests

def check_sitemap(website):
    """
    Check if the provided website has a sitemap.xml.

    Args:
        website (str): The URL of the website to be checked.

    Returns:
        str: 
            - "🟢" if a sitemap is found.
            - "🔴" if a sitemap is not found or if there's a request-related error.
            - "⚪" for any other unexpected errors.
    """
    try:
        response = requests.get(f"https://{website}/sitemap.xml", timeout=10)
        if response.status_code == 200:
            return "🟢"
        else:
            return "🔴"
    except requests.RequestException:
        # This block captures common request-related exceptions like timeout, connection errors, etc.
        return "🔴"
    except Exception as e:
        # This block captures any other unexpected exceptions and provides an alert.
        print(f"Unexpected error while checking the sitemap for {website}: {e}")
        return "⚪"
