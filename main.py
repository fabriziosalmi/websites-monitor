from checks.pagespeed_check import check_pagespeed
from checks.security_headers_check import check_security_headers
from checks.ssl_check import check_ssl_cert
from checks.domain_expiration_check import check_domain_expiration
from checks.cdn_check import check_cdn

# List of websites to test
websites = [
    'audiolibri.org',
    'get.domainsblacklists.com'
]

report_md = "# Websites Monitor\n"
report_md += "### Various Checks\n"
report_md += "| Site | PageSpeed | Security Headers | SSL | Domain Expiration | CDN |\n"
report_md += "|------|-----------|------------------|-----|-------------------|-----|\n"

for website in websites:
    pagespeed_score = check_pagespeed(website)
    security_headers_status = check_security_headers(website)
    ssl_status = check_ssl_cert(website)
    domain_expiration_status = check_domain_expiration(website)
    cdn_status = check_cdn(website)

    report_md += f"| {website} | {pagespeed_score} | {security_headers_status} | {ssl_status} | {domain_expiration_status} | {cdn_status} |\n"

# Save the report
with open("README.md", "w") as f:
    f.write(report_md)
