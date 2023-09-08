import requests

def check_content_type_headers(website):
    """
    Checks if the 'Content-Type' header of the website is set to 'text/html' 
    and has a character encoding specified.
    
    :param website: The website URL to check.
    :return: "🟢" if the header is properly set, "🔴" otherwise.
    """
    try:
        response = requests.get(f"https://{website}")
        content_type = response.headers.get('Content-Type', '')
        
        # Check for both 'text/html' and a character encoding
        if 'text/html' in content_type and 'charset=' in content_type:
            return "🟢"
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking Content-Type headers for {website}: {e}")
        return "🔴"
