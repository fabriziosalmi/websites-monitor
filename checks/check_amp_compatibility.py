from bs4 import BeautifulSoup

def check_amp_compatibility(html_content):
    """
    Check if the provided HTML content has AMP compatibility.

    Returns:
        "🟢" if AMP compatible
        "🔴" if not AMP compatible
    """
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Checking for both standard AMP tags: ⚡ and amp
        amp_html = soup.find_all("html", attrs={"⚡": ""}) or soup.find_all("html", attrs={"amp": ""})
        
        if amp_html:
            return "🟢"
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking AMP compatibility: {e}")
        # If an error occurs, we assume it's not AMP compatible for safety
        return "🔴"
