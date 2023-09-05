import requests

def check_cms_used(website):
    try:
        response = requests.get(f"https://{website}")
        if "wp-" in response.text:
            return "🟢 (WordPress)"
        elif "Drupal" in response.text:
            return "🟢 (Drupal)"
        elif "Joomla" in response.text:
            return "🟢 (Joomla)"
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking CMS for {website}: {e}")
        return "🔴"
