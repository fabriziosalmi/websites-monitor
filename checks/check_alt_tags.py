import requests
from bs4 import BeautifulSoup

def check_alt_tags(website):
    """
    Check if all the images on the website have alt tags.

    Returns:
        "🔴" if no image has an alt tag
        "🟠" if some images have alt tags and one or more doesn't
        "🟢" if all images have alt tags
    """

    try:
        response = requests.get(f"https://{website}", timeout=10)  # Adding a timeout of 10 seconds
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all('img')

        total_images = len(images)
        images_with_alt = sum(1 for img in images if img.get('alt'))

        # If no image has an alt tag
        if images_with_alt == 0:
            print(f"No images with alt tags found on {website}.")
            return "🔴"
        # If some images don't have an alt tag
        elif images_with_alt < total_images:
            print(f"{total_images - images_with_alt} images without alt tags found on {website}.")
            return "🟠"
        # If all images have alt tags
        else:
            return "🟢"
    except Exception as e:
        print(f"An error occurred while checking alt tags for {website}: {e}")
        return "🔴"
