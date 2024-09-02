import requests
from requests.exceptions import RequestException

def check_deprecated_libraries(js_links):
    """
    Checks the provided JavaScript links for deprecated libraries.

    Args:
        js_links (list): List of JS link URLs to check.

    Returns:
        str: 
            - "🟢" if no deprecated libraries are found.
            - "🔴" if any deprecated library is detected.
    """
    # This dictionary contains libraries and their associated deprecated patterns.
    # Each pattern is a string that's indicative of that library's version.
    deprecated_libraries_patterns = {
        "jQuery": ["jQuery v1.", "jQuery 1."],
        "AngularJS": ["angularjs v1.", "angular.version:{full:'1."],
        "MooTools": ["MooTools v1.", "MooTools.More v1."],
        "Backbone.js": ["Backbone.js 0.", "Backbone.js 1.0."],
        "Vue.js": ["Vue v0.", "Vue v1."],  # Assuming versions 0.x and 1.x are deprecated
        "React": ["React v0."]  # Assuming version 0.x is deprecated
    }

    for link in js_links:
        try:
            # Fetch the content of the JS file
            response = requests.get(link, timeout=10)
            response.raise_for_status()
            content = response.text

            # Check for deprecated patterns in the content
            for lib_name, patterns in deprecated_libraries_patterns.items():
                if any(pattern in content for pattern in patterns):
                    print(f"Deprecated library detected: {lib_name} in {link}")
                    return "🔴"

        except RequestException as e:
            print(f"Error fetching content from {link}: {e}")
            continue

    print("No deprecated libraries found in the provided JS links.")
    return "🟢"
