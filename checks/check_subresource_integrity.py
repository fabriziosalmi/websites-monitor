from bs4 import BeautifulSoup
from typing import Tuple

def check_subresource_integrity(html_content: str) -> Tuple[str, int]:
    """
    Check if the given HTML content uses Subresource Integrity (SRI) by looking for tags with the 'integrity' attribute.
    
    Args:
        html_content (str): The HTML content to be analyzed.
    
    Returns:
        tuple: A status symbol and a count of tags with the 'integrity' attribute.
            - "🟢" if at least one tag with 'integrity' is found.
            - "🔴" otherwise.
    """
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all tags with the 'integrity' attribute
    integrity_tags = soup.find_all(attrs={"integrity": True})

    # Return the status and the count of integrity tags found
    if integrity_tags:
        print(f"Found {len(integrity_tags)} tag(s) with the 'integrity' attribute.")
        return "🟢", len(integrity_tags)
    else:
        print("No tags with the 'integrity' attribute were found.")
        return "🔴", 0
