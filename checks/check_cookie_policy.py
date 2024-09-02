import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, Timeout, HTTPError

def check_cookie_policy(website):
    """
    Verify if the website has a cookie policy and it's accessible to users.
    
    Args:
        website (str): URL of the website to be checked.
    
    Returns:
        str: 
            - "🟢" if a cookie policy is found and accessible
            - "🔴" if no cookie policy is found or if it's inaccessible
            - "⚪" for any errors
    """
    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    headers = {
        'User-Agent': 'CookiePolicyChecker/1.0'
    }

    try:
        # Method 1: Direct page analysis for cookie policy
        response = requests.get(website, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Common keywords associated with cookie policies
        keywords = ["cookie policy", "cookie statement", "use of cookies", "privacy policy"]

        # Check for the presence of these keywords in anchor tags (links)
        anchors = soup.find_all('a', string=lambda text: text and any(keyword in text.lower() for keyword in keywords))
        if anchors:
            print(f"Cookie policy found in links for {website}.")
            return "🟢"

        # If not found in links, check if any of the keywords are present in the page's text
        page_text = soup.get_text().lower()
        if any(keyword in page_text for keyword in keywords):
            print(f"Cookie policy text found on the page for {website}.")
            return "🟢"

        # Method 2: Check for common cookie policy URLs (Fallback)
        # Common paths where cookie policies are found
        common_paths = ["/cookie-policy", "/cookies", "/privacy-policy", "/legal/cookies", "/legal/privacy-policy"]
        for path in common_paths:
            try:
                policy_response = requests.get(f"{website.rstrip('/')}{path}", headers=headers, timeout=5)
                if policy_response.status_code == 200:
                    print(f"Cookie policy found at {website.rstrip('/')}{path}.")
                    return "🟢"
            except (Timeout, HTTPError) as e:
                print(f"Timeout or HTTP error occurred while checking {website.rstrip('/')}{path}: {e}")
                continue
            except RequestException as e:
                print(f"Request-related error occurred while checking {website.rstrip('/')}{path}: {e}")
                continue

        print(f"No cookie policy found for {website}.")
        return "🔴"  # No cookie policy found

    except (Timeout, HTTPError) as e:
        print(f"Timeout or HTTP error occurred while checking cookie policy for {website}: {e}")
        return "⚪"
    except RequestException as e:
        print(f"Request-related error occurred while checking cookie policy for {website}: {e}")
        return "⚪"
    except Exception as e:
        print(f"An unexpected error occurred while checking cookie policy for {website}: {e}")
        return "⚪"
