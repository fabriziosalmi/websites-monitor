def check_deprecated_libraries(js_links):
    deprecated_libraries = ["jquery-1.", "angular-1.", "mootools-1."]
    for link in js_links:
        for lib in deprecated_libraries:
            if lib in link:
                return "🔴"
    return "🟢"
