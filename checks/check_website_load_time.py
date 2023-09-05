import time
import requests

def check_website_load_time(website):
    start_time = time.time()
    try:
        response = requests.get(f"https://{website}")
        elapsed_time = time.time() - start_time
        if elapsed_time < 2:
            return "🟢"
        elif elapsed_time < 4:
            return "🟠"
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking website load time for {website}: {e}")
        return "🔴"
