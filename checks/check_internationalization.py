import requests
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def check_internationalization(website: str) -> str:
    """
    Checks if a website has implemented internationalization (i18n) using the lang attribute.

    Args:
        website (str): The URL of the website to check.

    Returns:
        str:
           - "🟢" if i18n is detected
           - "⚪" if i18n is not detected or an error occurred.
    """
    try:
        response = requests.get(website, timeout = 10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        html_tag = soup.find("html")

        if html_tag and html_tag.has_attr("lang"):
            logger.info(f"Internationalization is enabled for {website}.")
            return "🟢"
        else:
           logger.info(f"Internationalization is not enabled for {website}.")
           return "⚪"

    except requests.exceptions.RequestException as e:
         logger.error(f"An error occurred while checking internationalization for {website}: {e}")
         return "⚪"
    except Exception as e:
         logger.error(f"An error occurred while checking internationalization: {e}")
         return "⚪"
