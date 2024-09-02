import requests
from requests.exceptions import RequestException, Timeout, HTTPError

def check_sitemap(website):
    """
    Check if the provided website has a sitemap.xml.

    Args:
        website (str): The URL of the website to be checked.

    Returns:
        str: 
            - "🟢" if a sitemap is found.
            - "🔴" if a sitemap is not found or if there's a request-related error.
            - "⚪" for any other unexpected errors.
    """
    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"
    
    # Commonly used sitemap paths
    sitemap_paths = [
        '/sitemap.xml',                # Default location
        '/sitemap_index.xml',          # Index file often used for multiple sitemaps
        '/sitemap/sitemap.xml',        # Common alternative path
        '/sitemap1.xml',               # Numbered sitemap for websites with multiple sitemaps
        '/sitemap-index.xml',          # Alternative index naming
        '/sitemap/sitemap-index.xml',  # Nested alternative index naming
        '/sitemap_index.xml.gz'        # Compressed sitemap file
    ]

    headers = {
        "User-Agent": "SitemapChecker/1.0"
    }

    try:
        # Iterate through common sitemap paths
        for path in sitemap_paths:
            response = requests.get(f"{website}{path}", headers=headers, timeout=10)
            
            # Check for a successful response
            if response.status_code == 200 and '<urlset' in response.text.lower():
                return "🟢"
        
        # If no sitemaps are found after checking all paths
        return "🔴"
    
    except (Timeout, HTTPError) as e:
        print(f"Timeout or HTTP error occurred while checking the sitemap for {website}: {e}")
        return "🔴"
    except RequestException as e:
        print(f"Request-related error occurred while checking the sitemap for {website}: {e}")
        return "🔴"
    except Exception as e:
        print(f"Unexpected error while checking the sitemap for {website}: {e}")
        return "⚪"
