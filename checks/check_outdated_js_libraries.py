import requests

def check_outdated_js_libraries(website):
    outdated_libraries = ['jquery-1.', 'angularjs-1.']
    try:
        response = requests.get(f"https://{website}")
        for lib in outdated_libraries:
            if lib in response.text:
                return "🔴"
        return "🟢"
    except Exception as e:
        print(f"An error occurred while checking outdated JS libraries for {website}: {e}")
        return "🔴"
