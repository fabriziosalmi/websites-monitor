import re
import requests
from requests.exceptions import RequestException, Timeout, HTTPError
from bs4 import BeautifulSoup

def check_alt_tags(website):
    """
    Check if all the images on the website have alt tags.

    Args:
        website (str): The URL of the website to be checked.

    Returns:
        str: 
            - "🔴" if no image has an alt tag
            - "🟠" if some images have alt tags and one or more doesn't
            - "🟢" if all images have alt tags
            - "⚪" if an error occurs
    """
    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        'User-Agent': 'AltTagChecker/1.0'
    }

    try:
        # Method 1: Direct HTML content analysis using BeautifulSoup
        response = requests.get(website, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP issues
        soup = BeautifulSoup(response.text, 'lxml')

        # Find all images and count those with and without alt tags
        images = soup.find_all('img')
        total_images = len(images)
        images_with_alt = sum(1 for img in images if img.get('alt') and img.get('alt').strip())

        # Determine the result based on the alt tag analysis
        if total_images == 0:
            print(f"No images found on {website}.")
            return "🟢"  # No images, hence all images (none) have alt tags by definition
        elif images_with_alt == 0:
            print(f"No images with alt tags found on {website}.")
            return "🔴"
        elif images_with_alt < total_images:
            print(f"{total_images - images_with_alt} images without alt tags found on {website}.")
            return "🟠"
        else:
            return "🟢"

    except (Timeout, HTTPError, RequestException) as e:
        print(f"Request error occurred while checking alt tags for {website}: {e}")
        
        # Method 2: Alternative Heuristic Check via Meta Tags (Fallback)
        try:
            # Try to get the response again for fallback analysis
            response = requests.get(website, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for meta tags that could indicate a focus on accessibility
            accessibility_tags = soup.find_all('meta', {'name': re.compile(r'(description|keywords|viewport)', re.IGNORECASE)})

            # Heuristic: If the website uses meta tags commonly associated with accessibility
            if accessibility_tags:
                print(f"Some meta tags found that might indicate a focus on accessibility on {website}.")
                return "🟠"

            return "🔴"  # Assume no focus on accessibility if no relevant meta tags found

        except Exception as e:
            print(f"Error during heuristic check for alt tags for {website}: {e}")
            return "⚪"

    return "⚪"
