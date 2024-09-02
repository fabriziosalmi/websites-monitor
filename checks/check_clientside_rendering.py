from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException, Timeout, HTTPError

def check_clientside_rendering(website, threshold=10):
    """
    Checks if a website relies heavily on client-side rendering by counting the number of script tags and other indicators.
    
    Args:
        website (str): The website URL to check.
        threshold (int): The threshold above which the number of scripts indicates heavy client-side rendering.

    Returns:
        str: 
            - "🟢" if the number of scripts is below the threshold
            - "🟠" if it's close to the threshold
            - "🔴" if above the threshold
            - "⚪" if an error occurs
    """
    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        'User-Agent': 'ClientSideRenderingChecker/1.0'
    }

    try:
        # Method 1: Check number of script tags
        response = requests.get(website, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        scripts = soup.find_all('script')

        num_scripts = len(scripts)

        # Method 2: Additional check for specific JavaScript libraries and frameworks (Fallback)
        # Check for common client-side frameworks that are heavy on client-side rendering
        frameworks = ['react', 'angular', 'vue', 'next', 'nuxt', 'svelte', 'ember', 'backbone']
        framework_detected = any(framework in str(script.get('src', '')).lower() or framework in (script.string or '').lower() for script in scripts for framework in frameworks)

        # Determine result based on number of script tags and framework detection
        if num_scripts > threshold or framework_detected:
            print(f"Heavy client-side rendering detected for {website}.")
            return "🔴"
        elif threshold - 3 <= num_scripts <= threshold:
            print(f"Moderate client-side rendering detected for {website}.")
            return "🟠"
        else:
            print(f"Minimal client-side rendering detected for {website}.")
            return "🟢"

    except (Timeout, HTTPError) as e:
        print(f"Timeout or HTTP error occurred while checking client-side rendering for {website}: {e}")
        return "⚪"
    except RequestException as e:
        print(f"Request-related error occurred while checking client-side rendering for {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking client-side rendering for {website}: {e}")
        return "⚪"
