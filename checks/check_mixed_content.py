from bs4 import BeautifulSoup
import requests

def check_mixed_content(website):
    """
    Check a given website for mixed content issues by searching for resources loaded over HTTP.
    
    Args:
    - website (str): The URL of the website to be checked.
    
    Returns:
    - str: "🟢" if no mixed content is found, "🔴" otherwise.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(f"https://{website}", headers=headers, stream=True)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for mixed content in src and href attributes
        mixed_content_src = soup.find_all(src=lambda x: x and x.startswith('http:'))
        mixed_content_href = soup.find_all(href=lambda x: x and x.startswith('http:'))
        
        if mixed_content_src or mixed_content_href:
            return "🔴"
        else:
            return "🟢"
    except Exception as e:
        print(f"An error occurred while checking for mixed content on {website}: {e}")
        return "🔴"  # Return red as a caution when an error occurs
