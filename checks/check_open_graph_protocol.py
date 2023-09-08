from bs4 import BeautifulSoup
import requests

def check_open_graph_protocol(website):
    """
    Check a given website for the presence of Open Graph Protocol meta tags.
    
    Args:
    - website (str): The URL of the website to be checked.
    
    Returns:
    - str: "🟢" if Open Graph Protocol meta tags are found, "🔴" otherwise.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(f"https://{website}", headers=headers, stream=True)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for the presence of essential Open Graph tags
        essential_tags = ['og:title', 'og:type', 'og:image', 'og:url']
        meta_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        
        if all(tag.attrs['property'] in essential_tags for tag in meta_tags):
            return "🟢"
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking Open Graph Protocol tags on {website}: {e}")
        return "🔴"  # Return red as a caution when an error occurs
from bs4 import BeautifulSoup
import requests

def check_open_graph_protocol(website):
    """
    Check a given website for the presence of Open Graph Protocol meta tags.
    
    Args:
    - website (str): The URL of the website to be checked.
    
    Returns:
    - str: "🟢" if Open Graph Protocol meta tags are found, "🔴" otherwise.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(f"https://{website}", headers=headers, stream=True)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for the presence of essential Open Graph tags
        essential_tags = ['og:title', 'og:type', 'og:image', 'og:url']
        meta_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        
        if all(tag.attrs['property'] in essential_tags for tag in meta_tags):
            return "🟢"
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking Open Graph Protocol tags on {website}: {e}")
        return "⚪"  # Return red as a caution when an error occurs
