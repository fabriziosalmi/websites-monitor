from bs4 import BeautifulSoup

def check_internationalization(html_content):
    """
    Check if the given HTML content supports internationalization by inspecting the 'lang' attribute.
    
    Args:
    - html_content (str): The HTML content to be checked.
    
    Returns:
    - str: "🟢" if the content supports internationalization, "🔴" otherwise.
    """
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check if the primary HTML tag has a lang attribute
        primary_lang = soup.html.attrs.get('lang')
        
        # Find other elements with a lang attribute
        lang_tags = soup.find_all(attrs={"lang": True})
        
        if primary_lang or len(lang_tags) > 1:
            return "🟢"
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking internationalization: {e}")
        return "⚪"
