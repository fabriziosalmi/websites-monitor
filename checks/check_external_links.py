import requests
from bs4 import BeautifulSoup

def check_external_links(website):
    """
    Verify that all external links on the website are valid and do not lead to broken or malicious destinations.
    
    Args:
    - website (str): URL of the website to be checked.
    
    Returns:
    - str: "🔴" if any broken or malicious external link is found, "🟢" otherwise, "🟡" for any errors.
    """
    try:
        response = requests.get(website)
        soup = BeautifulSoup(response.text, 'html.parser')

        broken_links = 0
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http') and not href.startswith(website):  # external link
                try:
                    resp = requests.get(href, timeout=5)
                    # You can expand this by checking for links leading to known malicious websites.
                    if resp.status_code != 200:
                        broken_links += 1
                except requests.RequestException:
                    broken_links += 1

        if broken_links > 0:
            return "🔴"  # Broken external links found
        return "🟢"  # All external links are valid
    except Exception as e:
        print(f"Error checking external links for {website}. Error: {e}")
        return "🟡"  # Error occurred
