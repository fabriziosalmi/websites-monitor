import requests
import logging
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

def check_deprecated_libraries(website: str) -> str:
    """
    Checks if a website is using deprecated JavaScript libraries.

    Args:
        website (str): The URL of the website to check.

    Returns:
         str:
            - "🟡" if deprecated libraries are found.
            - "🟢" if no deprecated libraries are found.
            - "⚪" if any errors occur during the check.
    """
    try:
      
        response = requests.get(f"https://{website}", timeout = 10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        scripts = soup.find_all('script', src=True)

        deprecated_libraries = {
            "jquery-migrate": "1.x",
            "prototype": "1.x",
            "modernizr": "2.x"
        }
        
        for script in scripts:
            src = script['src']
            for library, version in deprecated_libraries.items():
                if library in src:
                    logger.warning(f"Deprecated library {library} version {version} found in {website}.")
                    return "🟡"
            
        logger.info(f"No deprecated libraries found in the provided JS links.")
        return "🟢"
    
    except RequestException as e:
        logger.error(f"Error fetching content from {website}: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Error during deprecated library check for {website}: {e}")
        return "⚪"
