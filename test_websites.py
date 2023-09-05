import requests
import json
from datetime import datetime
import whois
import ssl
import socket

# Function to check domain expiration
def check_domain_expiration(domain):
    try:
        w = whois.whois(domain)
        expiration_date = w.expiration_date
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]
        days_to_expire = (expiration_date - datetime.now()).days

        if days_to_expire < 15:
            return "🔴"
        elif days_to_expire < 30:
            return "🟠"
        else:
            return "🟢"
    except Exception as e:
        print(f"An error occurred while checking domain expiration for {domain}: {e}")
        return "🔴"

# Function to check SSL certificate
def check_ssl_cert(host, port=443):
    try:
        context = ssl.create_default_context()
        conn = socket.create_connection((host, port))
        sock = context.wrap_socket(conn, server_hostname=host)
        cert = sock.getpeercert()
        sock.close()

        cert_expiry = datetime.strptime(cert['notAfter'], r"%b %d %H:%M:%S %Y %Z")
        days_to_expire = (cert_expiry - datetime.utcnow()).days

        if days_to_expire <= 0:
            return "🔴"
        elif days_to_expire <= 30:
            return "🟠"
        else:
            return "🟢"
    except (ssl.SSLError, ssl.CertificateError):
        return "🔴"

# Function to check for popular CDNs in headers
def check_cdn(headers):
    cdn_headers = [
        ("Server", "cloudflare"),
        ("X-hello-human", "KeyCDN"),
        ("X-CDN", "stackpath"),
        ("X-Cache", "Fastly")
    ]
    for header, value in cdn_headers:
        if header in headers and value.lower() in headers[header].lower():
            return "🟢"
    return "🟠"

# List of websites to test
websites = [
    'audiolibri.org',
    'get.domainsblacklists.com'
]

# Initialize Markdown report with table header
report_md = "# Websites monitor\n### Performances, headers, SSL/TLS, domain expiration and CDN enablement monitoring checks via Github action.\n| Site | Performances | CSP | Headers | SSL | Expiration | CDN |\n|------|-----------------|--------------------------|------------------|-----|--------|-----|\n"

for website in websites:
    # PageSpeed API
    pagespeed_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://{website}"
    pagespeed_response = requests.get(pagespeed_url)
    pagespeed_data = json.loads(pagespeed_response.text)
    pagespeed_score = pagespeed_data["lighthouseResult"]["categories"]["performance"]["score"] * 100

    # Security Headers Check
    security_response = requests.get(f"https://{website}")
    headers = security_response.headers

    # Determine CSP Status
    csp_status = "🟢" if headers.get('Content-Security-Policy') else "🔴"

    # Check for revealing headers
    revealing_status = "🟢" if not any(header in headers for header in ['Server', 'X-Powered-By', 'X-AspNet-Version']) else "🔴"

    # Check SSL Certificate
    ssl_status = check_ssl_cert(website)

    # Check Domain Expiration
    domain_status = check_domain_expiration(website)

    # Check CDN
    cdn_status = check_cdn(headers)

    # Update Markdown report with table row data
    report_md += f"| {website} | {pagespeed_score} | {csp_status} | {revealing_status} | {ssl_status} | {domain_status} | {cdn_status} |\n"

# Get the current time and format it as a string
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Add a "Last Updated" timestamp to the Markdown report
report_md += f"\n---\nLast Updated: {current_time}"

# Save report to a Markdown file
with open("README.md", "w") as f:
    f.write(report_md)
