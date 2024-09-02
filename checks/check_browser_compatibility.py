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
    options = webdriver.ChromeOptions()
    options.headless = True  # Run in headless mode for better performance

    # List of drivers to test compatibility
    driver_classes = [
        (webdriver.Chrome, webdriver.ChromeOptions),
        (webdriver.Firefox, webdriver.FirefoxOptions),
        (webdriver.Safari, None)  # Safari does not require options for headless mode
    ]

    try:
        for driver_class, options_class in driver_classes:
            try:
                # Set up options for each driver
                if options_class:
                    browser_options = options_class()
                    browser_options.headless = True
                    driver = driver_class(options=browser_options)
                else:
                    driver = driver_class()

                driver.get(website)

                # Basic check: Ensure that the page has a title element
                if 'title' not in driver.page_source.lower():
                    driver.quit()
                    print(f"Compatibility issue found with {driver.name} for {website}.")
                    return "🔴"

                driver.quit()

            except WebDriverException as e:
                print(f"Error occurred while testing {driver_class.__name__} for {website}: {e}")
                continue  # Continue to the next browser if one fails

        print(f"Website {website} is compatible with all tested browsers.")
        return "🟢"

    except Exception as e:
        print(f"An unexpected error occurred while checking browser compatibility for {website}: {e}")
        return "🔴"
