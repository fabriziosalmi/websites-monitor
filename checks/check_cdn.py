def check_cdn(headers):
    """
    Checks the provided HTTP headers for signs of popular Content Delivery Networks (CDNs).

    :param headers: Dictionary of HTTP headers.
    :return: "🟢" if a known CDN is detected, "🔴" if no CDN is detected.
    """
    # Mapping of headers to sets of possible CDN indicators
    cdn_headers = {
        "Server": {"cloudflare", "keycdn", "akamai", "fastly", "gcore", "maxcdn", "incapsula", "sucuri", "imperva"},
        "X-CDN": {"stackpath", "akamai", "section-io", "cachefly"},
        "X-Cache": {"fastly", "cloudfront", "cdn-cache", "cachefly", "squid"},
        "X-Powered-By": {"cdn77", "edgecast", "keycdn"},
        "CF-Cache-Status": {"hit", "miss", "expired", "revalidated"},  # Cloudflare-specific
        "X-Cache-Status": {"hit", "miss", "stale", "updating"},
        "X-Akamai-Transformed": {"9xx-xml", "9xx-proxy", "9xx-push"},  # Akamai-specific
        "X-Edge-IP": {"akamai"},
        "X-Edge-Location": {"akamai"},
        "Via": {"akamai", "cloudflare", "fastly", "cloudfront", "section.io"},
        "X-Proxy-Cache": {"hit", "miss"},
        "CDN-Cache-Control": {"max-age", "no-cache", "public"},  # General CDN caching
    }

    # Convert headers to lowercase for case-insensitive comparison
    headers_lower = {k.lower(): v.lower() for k, v in headers.items()}

    # Check for CDN indicators in headers
    for header, possible_values in cdn_headers.items():
        header_value = headers_lower.get(header.lower(), "")
        if any(cdn_value in header_value for cdn_value in possible_values):
            return "🟢"

    return "🔴"
