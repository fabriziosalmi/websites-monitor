import json
from datetime import datetime
from checks.check_pagespeed import check_pagespeed
from checks.check_security_headers import check_security_headers
from checks.check_ssl_cert import check_ssl_cert
from checks.check_domain_expiration import check_domain_expiration
from checks.check_cdn import check_cdn

# Read websites from external file
with open('websites.txt', 'r') as f:
    websites = [line.strip() for line in f.readlines()]

# Initialize Markdown report with table header and project description
report_md = "# Websites Monitor\n"
report_md += "## Project Description\n"
report_md += "This project aims to continuously monitor various aspects of specified websites. "
report_md += "It checks performances, security headers, SSL/TLS certificates, domain expiration, and CDN enablement. "
report_md += "The GitHub action is scheduled to run once a day and updates this README with the latest results.\n"
report_md += "\n## How to Use\n"
report_md += "1. Fork this repository.\n"
report_md += "2. Add the websites you want to monitor in the `websites.txt` file, one per line.\n"
report_md += "3. Enable GitHub Actions if not already enabled.\n"
report_md += "4. The README will be automatically updated with the latest check results once a day.\n"
report_md += "\n### Monitoring Checks\n"
report_md += "| Site | Performances | CSP | Headers | SSL | Expiration | CDN |\n"
report_md += "|------|-----------------|--------------------------|------------------|-----|--------|-----|\n"

for website in websites:
    pagespeed_score = check_pagespeed(website)
    csp_status, revealing_status = check_security_headers(website)
    ssl_status = check_ssl_cert(website)
    domain_status = check_domain_expiration(website)
    cdn_status = check_cdn(website)

    # Update Markdown report with table row data
    report_md += f"| {website} | {pagespeed_score} | {csp_status} | {revealing_status} | {ssl_status} | {domain_status} | {cdn_status} |\n"

# Get the current time and format it as a string
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Add a "Last Updated" timestamp to the Markdown report
report_md += f"\n---\nLast Updated: {current_time}"

# Save report to a Markdown file
with open("README.md", "w") as f:
    f.write(report_md)
