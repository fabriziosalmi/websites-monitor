import requests
from urllib.parse import urlparse

def check_third_party_resources(website):
    """
    Check for third-party resources loaded by the website.
    
    Args:
    - website (str): URL of the website to be checked.
    
    Returns:
    - str: "🟢" if the number of third-party resources is minimal,
           "🟠" if moderate number of third-party resources,
           "🔴" if high number of third-party resources,
           "⚪" for any errors.
    """
    
    try:
        # List to store the domains of third-party resources
        third_party_domains = []

        # Fetch the content of the page
        response = requests.get(website)
        response_content = response.content.decode('utf-8')
        
        # Simple checks for third party scripts, styles, and images
        # This is a basic approach and can be refined further with HTML parsing libraries
        for line in response_content.split("\n"):
            if any(tag in line for tag in ["<script", "<link", "<img"]):
                resource_url = line.split("src=")[1].split('"')[1] if "src=" in line else line.split("href=")[1].split('"')[1]
                domain = urlparse(resource_url).netloc
                
                if domain and domain != urlparse(website).netloc:
                    third_party_domains.append(domain)

        third_party_count = len(set(third_party_domains))
        
        # Depending on the count of third-party resources, return the status
        if third_party_count == 0:
            return "🟢"
        elif third_party_count <= 5:
            return "🟠"
        else:
            return "🔴"

    except Exception as e:
        print(f"Error occurred: {e}")
        return "⚪"
