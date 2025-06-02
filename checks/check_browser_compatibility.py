from selenium import webdriver
from selenium.common.exceptions import WebDriverException

def check_browser_compatibility(website):
    """
    Check if the website is compatible with different browsers.

    Args:
        website (str): The URL of the website to be checked.

    Returns:
        str: 
            - "🟢" if the website is compatible with all tested browsers
            - "🔴" if the website is not compatible with any browser or if an error occurs
    """
    # Ensure the website starts with 'http://' or 'https://'
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    # List of drivers to test compatibility
    driver_configs = [
        ("Chrome", webdriver.Chrome, webdriver.ChromeOptions),
        ("Firefox", webdriver.Firefox, webdriver.FirefoxOptions),
    ]

    compatible_browsers = 0
    total_browsers = len(driver_configs)

    for browser_name, driver_class, options_class in driver_configs:
        driver = None
        try:
            # Set up options for each driver
            browser_options = options_class()
            browser_options.add_argument('--headless')  # Run in headless mode
            browser_options.add_argument('--no-sandbox')
            browser_options.add_argument('--disable-dev-shm-usage')
            
            driver = driver_class(options=browser_options)
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
    if compatible_browsers == total_browsers:
        return "🟢"
    elif compatible_browsers > 0:
        return "🟠"  # Partially compatible
    else:
        return "🔴"
