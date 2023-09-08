import requests

def check_robot_txt(website):
    """
    Verify the presence and basic validity of a robots.txt file on a website.
    
    Args:
    - website (str): The URL (without protocol) of the website to check.
    
    Returns:
    - str: "🟢" if the site has a valid robots.txt file, "🔴" otherwise, and 
           "⚪" in case of an error.
    """
    headers = {
        "User-Agent": "RobotsTxtChecker/1.0"
    }

    try:
        response = requests.get(f"https://{website}/robots.txt", headers=headers)
        content = response.text

        # Check for 200 status code and presence of specific directives
        if response.status_code == 200 and ("User-agent" in content or "Disallow" in content):
            return "🟢"
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking robots.txt for {website}: {e}")
        return "⚪"
