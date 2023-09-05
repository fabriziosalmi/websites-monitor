from selenium import webdriver

def check_browser_compatibility(website):
    try:
        drivers = [webdriver.Chrome(), webdriver.Firefox(), webdriver.Safari()]
        for driver in drivers:
            driver.get(website)
            if not 'title' in driver.page_source.lower():
                return "🔴"
        return "🟢"
    except:
        return "🔴"
