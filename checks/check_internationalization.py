from bs4 import BeautifulSoup

def check_internationalization(html_content: str) -> str:
    """
    Check if the given HTML content supports internationalization by inspecting the 'lang' attribute.

    Args:
        html_content (str): The HTML content to be checked.

    Returns:
        str:
            - "🟢" if the content supports internationalization.
            - "🔴" if the content does not support internationalization.
            - "⚪" if an unexpected error occurs.
    """
    try:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Check if the primary <html> tag has a 'lang' attribute
        primary_lang = soup.html.attrs.get('lang', None)

        # Find all elements with a 'lang' attribute
        lang_tags = soup.find_all(attrs={"lang": True})

        # Check for the presence of the 'lang' attribute in <html> or in any other tags
        if primary_lang:
            print("Primary HTML tag has a 'lang' attribute.")
            return "🟢"
        elif len(lang_tags) > 1:  # Check if there are other tags with 'lang' attributes
            print(f"Found {len(lang_tags)} elements with 'lang' attribute.")
            return "🟢"
        else:
            print("No 'lang' attribute found in primary HTML tag or other elements.")
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking internationalization: {e}")
        return "⚪"
