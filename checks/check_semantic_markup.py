from bs4 import BeautifulSoup

def check_semantic_markup(html_content):
    """
    Check if the provided HTML content contains semantic markup 
    in the form of JSON-LD or Microdata.

    Args:
        html_content (str): The HTML content to be checked.

    Returns:
        str: "🟢" if semantic markup is found, "🔴" otherwise.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Check for JSON-LD semantic markup
    json_ld = soup.find(type="application/ld+json")
    
    # Check for Microdata semantic markup
    microdata = soup.find(attrs={"itemscope": True})
    
    if json_ld or microdata:
        return "🟢"
    return "🔴"
