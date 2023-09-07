from datetime import datetime
from checks.check_pagespeed_performances import check_pagespeed_performances
from checks.check_security_headers import check_security_headers
from checks.check_ssl_cert import check_ssl_cert
from checks.check_domain_expiration import check_domain_expiration
from checks.check_cdn import check_cdn
from checks.check_dns_blacklist import check_dns_blacklist
from checks.check_alt_tags import check_alt_tags
from checks.check_cors_headers import check_cors_headers
from checks.check_cookie_flags import check_cookie_flags
from checks.check_hsts import check_hsts
from checks.check_open_graph_protocol import check_open_graph_protocol
from checks.check_privacy_protected_whois import check_privacy_protected_whois
from checks.check_privacy_exposure import check_privacy_exposure
from checks.check_robot_txt import check_robot_txt
from checks.check_sitemap import check_sitemap
from checks.check_semantic_markup import check_semantic_markup
from checks.check_subdomain_enumeration import check_subdomain_enumeration
from checks.check_website_load_time import check_website_load_time
from checks.check_xss_protection import check_xss_protection
from checks.check_domain_breach import check_domain_breach

# Read websites from external file
with open('websites.txt', 'r') as f:
    websites = [line.strip() for line in f.readlines()]

# Initialize Markdown report
report_md = "# Websites Monitor\n"

# Add project description
report_md += "## Project Description\n"
report_md += "This project aims to continuously monitor various aspects of specified websites. "
report_md += "It runs a variety of checks, ranging from performance to security considerations. "
report_md += "The GitHub Action is scheduled to run once per day, updating this README with the latest results.\n"

# Add usage instructions
report_md += "\n## How to Use\n"
report_md += "1. Fork this repository.\n"
report_md += "2. Add the websites you want to monitor in the `websites.txt` file, one per line.\n"
report_md += "3. Enable GitHub Actions if not already enabled.\n"
report_md += "4. The README will be automatically updated with the latest check results once a day.\n"

# Initialize the table
report_md += "\n### Monitoring Checks\n"
report_md += "| Check Type | " + " | ".join(websites) + " |\n"
report_md += "|------------|" + "---|" * len(websites) + "\n"

# List of check functions and their human-readable names
check_functions = [
    ("Pagespeed Performances", check_pagespeed_performances),
    ("Headers", check_security_headers),
    ("SSL Expiration", check_ssl_cert),
    ("Domain Expiration", check_domain_expiration),
    ("CDN", check_cdn),
    ("DNS Blacklists (Spamhaus + Spamcop)", check_dns_blacklist),
    ("Alt Tags", check_alt_tags),
    ("CORS Headers", check_cors_headers),
    ("Cookie Flags", check_cookie_flags),
    ("HSTS", check_hsts),
    ("Open Graph Protocol", check_open_graph_protocol),
    ("Privacy-Protected Whois", check_privacy_protected_whois),
    ("Privacy Exposure", check_privacy_exposure),
    ("Robots.txt", check_robot_txt),
    ("Sitemap", check_sitemap),
    ("Semantic Markup", check_semantic_markup),
    ("Subdomain Enumeration", check_subdomain_enumeration),
    ("Website Load Time", check_website_load_time),
    ("XSS Protection", check_xss_protection),
    ("Domain breach", check_domain_breach),
]

# Populate the table with check results
for check_name, check_func in check_functions:
    report_md += f"| {check_name} | "
    for website in websites:
        result = check_func(website)
        report_md += f"{result} | "
    report_md += "\n"

# Timestamp
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
report_md += f"\n---\nLast Updated: {current_time}\n"

# Write the Markdown report to a file
with open("README.md", "w") as f:
    f.write(report_md)
