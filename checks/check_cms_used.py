import requests

def check_cms_used(website):
    """
    Checks which CMS (if any) is used by a website based on certain telltale patterns in its content.
    
    :param website: The website URL to check.
    :return: "🟢 (CMS Name)" if a CMS is detected, "🔴" otherwise.
    """
    cms_patterns = {
        "WordPress": ["wp-", "wp-content", "wp-includes"],
        "Drupal": ["Drupal", "sites/default/files"],
        "Joomla": ["Joomla", "/templates/joomla/"]
    }

    try:
        response = requests.get(f"https://{website}")
        content = response.text
        
        for cms, patterns in cms_patterns.items():
            if any(pattern in content for pattern in patterns):
                return f"🟢 ({cms})"
        
        return "🔴"
    except Exception as e:
        print(f"An error occurred while checking CMS for {website}: {e}")
        return "⚪"
