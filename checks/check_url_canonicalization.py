import requests
from bs4 import BeautifulSoup
from typing import Optional

def check_url_canonicalization(website: str) -> str:
    """
    Check if the given website uses a canonical link element to avoid potential duplicate content issues.
    
    Args:
    - website (str): The URL of the website to be checked.
    
    Returns:
    - str: "🟢" if a correct canonical link element is found,
           "🔴" otherwise.
    """
    try:
        response_url = f"https://{website}"
        response = requests.get(response_url)
        
        if response.status_code != 200:
            return "🔴"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        canonical_tag = soup.find('link', {'rel': 'canonical'})
        
        if canonical_tag and canonical_tag.get('href') == response_url:
            return "🟢"
        else:
            return "🔴"
            
    except requests.RequestException as e:
        print(f"An error occurred while checking URL canonicalization for {website}: {e}")
        return "🔴"

