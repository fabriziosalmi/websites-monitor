import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def check_third_party_requests(website):
    """
    Monitor the number of third-party requests made by a website.
    Args:
    - website (str): URL of the website to be checked.
    
    Returns:
    - str: "🔴" if the website makes a high number of third-party requests, "🟢" otherwise, "🟡" for any errors.
    """
    try:
        response = requests.get(website)
        parsed_url = urlparse(website)
        main_domain = parsed_url.netloc

        soup = BeautifulSoup(response.text, 'html.parser')
        
        third_party_requests = 0

        for tag in soup.find_all(['link', 'script', 'img']):
            href = tag.get('href') or tag.get('src')
            if href:
                parsed_href = urlparse(href)
                if parsed_href.netloc and parsed_href.netloc != main_domain:
                    third_party_requests += 1

        # For this example, let's assume more than 50 third-party requests is considered high.
        # Adjust this value as per your requirements.
        if third_party_requests > 50:
            return "🔴"  # Many third-party requests
        return "🟢"  # Acceptable number of third-party requests
    except Exception as e:
        print(f"Error checking third-party requests for {website}. Error: {e}")
        return "🟡"  # Error occurred

