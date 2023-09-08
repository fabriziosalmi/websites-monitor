def check_cdn(headers):
    """
    Checks the provided HTTP headers for signs of popular Content Delivery Networks (CDNs).
    
    :param headers: Dictionary of HTTP headers.
    :return: "🟢" if a known CDN is detected, "🟠" if unsure, and "🔴" if no CDN is detected.
    """
    
    cdn_headers = {
        "Server": ["cloudflare", "KeyCDN"],
        "X-CDN": ["stackpath", "Akamai"],
        "X-Cache": ["Fastly"],
        "X-Powered-By": ["CDN77"],
        "X-hello-human": ["KeyCDN"]
    }

    for header, possible_values in cdn_headers.items():
        if header in headers:
            for value in possible_values:
                if value.lower() in headers[header].lower():
                    return "🟢"
    
    # If the function hasn't returned by now, it means no known CDN was detected.
    return "🔴"
