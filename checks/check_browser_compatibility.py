import os
import shutil
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

# Browser executables looked up before starting Selenium. Without a browser
# Selenium Manager downloads a driver that cannot run (e.g. in the slim Docker
# image: "chromedriver unexpectedly exited. Status code was: 127"), which is
# slow and says nothing about the website.
BROWSER_EXECUTABLES = {
    "Chrome": {
        "names": ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"],
        "paths": ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                  "/Applications/Chromium.app/Contents/MacOS/Chromium"],
    },
    "Firefox": {
        "names": ["firefox", "firefox-esr"],
        "paths": ["/Applications/Firefox.app/Contents/MacOS/firefox"],
    },
}


def _browser_installed(browser_name):
    """Return True if an executable for the browser can be found locally."""
    executables = BROWSER_EXECUTABLES.get(browser_name, {})
    if any(shutil.which(name) for name in executables.get("names", [])):
        return True
    return any(os.path.exists(path) for path in executables.get("paths", []))


def check_browser_compatibility(website):
    """
    Check if the website is compatible with different browsers.

    Args:
        website (str): The URL of the website to be checked.

    Returns:
        str: 
            - "🟢" if the website is compatible with all tested browsers
            - "🟠" if the website loads in some of the browsers that could start
            - "🔴" if the website is not compatible with any browser that could start
            - "⚪ (no browser available)" if no browser is installed or none could start
    """
    # Guard against empty or whitespace-only input
    if not website or not website.strip():
        return "🔴"

    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    # List of drivers to test compatibility
    driver_configs = [
        ("Chrome", webdriver.Chrome, webdriver.ChromeOptions),
        ("Firefox", webdriver.Firefox, webdriver.FirefoxOptions),
    ]

    compatible_browsers = 0
    total_browsers = 0  # browsers that actually started

    for browser_name, driver_class, options_class in driver_configs:
        if not _browser_installed(browser_name):
            print(f"{browser_name} is not installed, skipping.")
            continue
        driver = None
        try:
            # Set up options for each driver
            browser_options = options_class()
            browser_options.add_argument('--headless')  # Run in headless mode
            browser_options.add_argument('--no-sandbox')
            browser_options.add_argument('--disable-dev-shm-usage')
            
            try:
                driver = driver_class(options=browser_options)
            except Exception as e:
                # The driver could not start: no verdict on the website
                print(f"{browser_name} could not start: {str(e).splitlines()[0] if str(e) else e}")
                continue
            total_browsers += 1
            driver.set_page_load_timeout(10)  # Set timeout for page load
            
            driver.get(website)

            # Basic check: Ensure that the page loads successfully and has content
            if driver.title and len(driver.page_source) > 100:
                print(f"Website {website} is compatible with {browser_name}.")
                compatible_browsers += 1
            else:
                print(f"Compatibility issue found with {browser_name} for {website}.")

        except WebDriverException as e:
            print(f"Error occurred while testing {browser_name} for {website}: {e}")
        except Exception as e:
            print(f"Unexpected error with {browser_name} for {website}: {e}")
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass  # Ignore cleanup errors

    # Determine result based on browser compatibility
    if total_browsers == 0:
        return "⚪ (no browser available)"
    if compatible_browsers == total_browsers:
        return "🟢"
    elif compatible_browsers > 0:
        return "🟠"  # Partially compatible
    else:
        return "🔴"
