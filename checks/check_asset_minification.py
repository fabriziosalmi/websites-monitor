import requests
from requests.exceptions import RequestException, Timeout, HTTPError
from bs4 import BeautifulSoup
import re

def check_asset_minification(website):
    """
    Check if the website's CSS/JS assets are minified.

    Args:
        website (str): URL of the website to be checked.

    Returns:
        str: 
            - "🟢" if all assets are minified
            - "🟠" if some assets are minified and others are not
            - "🔴" if none of the assets are minified
            - "⚪" if an error occurs or no assets to check
    """
    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        'User-Agent': 'AssetMinificationChecker/1.0'
    }

    try:
        # First, get the website content to extract asset links
        response = requests.get(website, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Extract CSS and JS links
        css_links = [link.get('href') for link in soup.find_all('link', rel='stylesheet') if link.get('href')]
        js_links = [script.get('src') for script in soup.find_all('script', src=True) if script.get('src')]
        
        # Convert relative URLs to absolute
        from urllib.parse import urljoin
        website_links = []
        for link in css_links + js_links:
            if link.startswith(('http://', 'https://')):
                website_links.append(link)
            else:
                website_links.append(urljoin(website, link))

        minified_count = 0
        total_assets = 0

        for link in website_links:
            try:
                # Method 1: Check content and minification status
                asset_response = requests.get(link, headers=headers, timeout=10)
                asset_response.raise_for_status()

                # Check if the content type is either CSS or JavaScript
                content_type = asset_response.headers.get('Content-Type', '').lower()
                if 'text/css' in content_type or 'javascript' in content_type:
                    total_assets += 1
                    content = asset_response.text

                    # Check for minification indicators
                    # Minified files typically have very long lines and no whitespace
                    lines = content.splitlines()
                    avg_line_length = sum(len(line) for line in lines) / max(len(lines), 1)
                    has_comments = '//' in content or '/*' in content
                    has_excessive_whitespace = re.search(r'\n\s*\n\s*\n', content)

                    # Heuristic: likely minified if average line length is high and no comments/whitespace
                    if avg_line_length > 200 and not has_comments and not has_excessive_whitespace:
                        minified_count += 1
                    else:
                        print(f"Asset at {link} appears not to be minified.")

            except (Timeout, HTTPError, RequestException) as e:
                print(f"Error while fetching content from {link}: {e}")
                continue

        # Determine the result based on the minification analysis
        if total_assets == 0:
            print(f"No CSS/JS assets found on {website}.")
            return "⚪"
        elif minified_count == 0:
            print("None of the assets are minified.")
            return "🔴"
        elif minified_count < total_assets:
            print(f"Some assets are minified, others are not. Minified: {minified_count}, Total: {total_assets}")
            return "🟠"
        else:
            print("All assets are minified.")
            return "🟢"

    except (Timeout, HTTPError, RequestException) as e:
        print(f"Request error occurred while checking asset minification for {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking asset minification for {website}: {e}")
        return "⚪"
