from bs4 import BeautifulSoup
from bs4 import FeatureNotFound

def check_semantic_markup(html_content):
    """
    Check if the provided HTML content contains semantic markup 
    in the form of JSON-LD, Microdata, or RDFa.

    Args:
        html_content (str): The HTML content to be checked.

    Returns:
        str: "🟢" if semantic markup is found, "🔴" otherwise.
    """
    # Prefer lxml parser for better performance, fallback to html.parser
    try:
        soup = BeautifulSoup(html_content, 'lxml')
    except FeatureNotFound:
        soup = BeautifulSoup(html_content, 'html.parser')
    
    # Check for JSON-LD semantic markup
    json_ld = soup.find('script', type="application/ld+json")
    
    # Check for Microdata semantic markup
    microdata = soup.find(attrs={"itemscope": True})
    
    # Check for RDFa semantic markup
    rdfa = soup.find_all(attrs={"vocab": True}) or soup.find_all(attrs={"typeof": True})

    if json_ld or microdata or rdfa:
        return "🟢"
    return "🔴"
