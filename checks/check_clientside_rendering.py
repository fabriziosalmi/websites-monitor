from bs4 import BeautifulSoup
import requests

def check_clientside_rendering(website, threshold=10):
    """
    Checks if a website relies heavily on client-side rendering by counting the number of script tags.
    
    :param website: The website URL to check.
    :param threshold: The threshold above which the number of scripts indicates heavy client-side rendering.
    :return: "🟢" if the number of scripts is below the threshold, "🟠" if it's close to the threshold, "🔴" if above.
    """
    try:
        response = requests.get(f"https://{website}")
        soup = BeautifulSoup(response.content, 'html.parser')
        scripts = soup.find_all('script')
        
        num_scripts = len(scripts)
        
        if num_scripts > threshold:
            return "🔴"
        elif threshold - 3 <= num_scripts <= threshold:
            return "🟠"
        else:
            return "🟢"
    except Exception as e:
        print(f"An error occurred while checking client-side rendering for {website}: {e}")
        return "🔴"
