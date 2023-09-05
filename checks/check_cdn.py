def check_cdn(headers):
    cdn_headers = [
        ("Server", "cloudflare"),
        ("Server", "KeyCDN"),
        ("X-CDN", "stackpath"),
        ("X-Cache", "Fastly"),
        ("X-CDN", "Akamai"),
        ("X-Powered-By", "CDN77"),
        ("X-hello-human", "KeyCDN")
    ]
    for header, value in cdn_headers:
        if header in headers and value.lower() in headers[header].lower():
            return "🟢"
    return "🟠"
