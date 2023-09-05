import requests

def check_robot_txt(website):
    try:
        response = requests.get(f"https://{website}/robots.txt")
        if response.status_code == 200:
            return "🟢"
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking robots.txt for {website}: {e}")
        return "🔴"
