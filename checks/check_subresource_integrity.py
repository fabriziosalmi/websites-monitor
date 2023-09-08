from bs4 import BeautifulSoup
from typing import Tuple

def check_subresource_integrity(html_content: str) -> Tuple[str, int]:
    """
    Check if the given HTML content uses Subresource Integrity (SRI) by looking for tags with the 'integrity' attribute.
    
    Args:
    - html_content (str): The HTML content to be analyzed.
    
    Returns:
    - tuple: A status symbol and a count of tags with the 'integrity' attribute.
             "🟢" if at least one tag with 'integrity' is found,
             "🔴" otherwise.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    integrity_tags = soup.find_all(attrs={"integrity": True})
    
    return "🟢" if integrity_tags else "🔴", len(integrity_tags)

