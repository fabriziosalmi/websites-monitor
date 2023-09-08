import requests

def check_cookie_flags(website):
    try:
        response = requests.get(f"https://{website}")
        set_cookie_headers = response.headers.getlist('Set-Cookie')
        
        all_secure_http_only = True
        any_secure_http_only = False
        
        for cookie_header in set_cookie_headers:
            if 'Secure' in cookie_header and 'HttpOnly' in cookie_header:
                any_secure_http_only = True
            else:
                all_secure_http_only = False
        
        # All cookies have Secure and HttpOnly flags
        if all_secure_http_only:
            return "🟢"
        # Some cookies have Secure and HttpOnly flags, but not all
        elif any_secure_http_only:
            return "🟠"
        # No cookies have both Secure and HttpOnly flags
        else:
            return "🔴"
    except Exception as e:
        print(f"An error occurred while checking cookie flags for {website}: {e}")
        return "⚪"
