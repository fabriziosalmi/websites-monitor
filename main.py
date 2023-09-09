from datetime import datetime
from checks.check_domain_breach import check_domain_breach
from checks.check_domain_expiration import check_domain_expiration
from checks.check_ssl_cert import check_ssl_cert
from checks.check_dns_blacklist import check_dns_blacklist
from checks.check_domainsblacklists_blacklist import check_domainsblacklists_blacklist
from checks.check_security_headers import check_security_headers
from checks.check_hsts import check_hsts
from checks.check_xss_protection import check_xss_protection
from checks.check_redirect_chains import check_redirect_chains
from checks.check_pagespeed_performances import check_pagespeed_performances
from checks.check_website_load_time import check_website_load_time
from checks.check_rate_limiting import check_rate_limiting
from checks.check_cdn import check_cdn
from checks.check_brotli_compression import check_brotli_compression
from checks.check_deprecated_libraries import check_deprecated_libraries
from checks.check_clientside_rendering import check_clientside_rendering
from checks.check_mixed_content import check_mixed_content
from checks.check_content_type_headers import check_content_type_headers
from checks.check_internationalization import check_internationalization
from checks.check_floc import check_floc
from checks.check_amp_compatibility import check_amp_compatibility
from checks.check_robot_txt import check_robot_txt
from checks.check_sitemap import check_sitemap
from checks.check_favicon import check_favicon
from checks.check_alt_tags import check_alt_tags
from checks.check_open_graph_protocol import check_open_graph_protocol
from checks.check_semantic_markup import check_semantic_markup
from checks.check_alt_tags import check_alt_tags
from checks.check_ad_and_tracking import check_ad_and_tracking
from checks.check_privacy_protected_whois import check_privacy_protected_whois
from checks.check_privacy_exposure import check_privacy_exposure
# testing..
# from checks.check_ssl_cipher_strength import check_ssl_cipher_strength
# from checks.check_cors_headers import check_cors_headers
# from checks.check_cookie_flags import check_cookie_flags
# from checks.check_cookie_policy import check_cookie_policy
# from checks.check_cookie_duration import check_cookie_duration
# from checks.check_cookie_samesite_attribute import check_cookie_samesite_attribute
# from checks.check_subdomain_enumeration import check_subdomain_enumeration
# from checks.check_asset_minification import check_asset_minification
# from checks.check_broken_links import check_broken_links
# from checks.check_browser_compatibility import check_browser_compatibility
# from checks.check_dnssec import check_dnssec
# from checks.check_external_links import check_external_links
# from checks.check_mobile_friendly import check_mobile_friendly
# from checks.check_server_response_time import check_server_response_time
# from checks.check_subresource_integrity import check_subresource_integrity
# from checks.check_third_party_requests import check_third_party_requests
# from checks.check_third_party_resources import check_third_party_resources
# from checks.check_url_canonicalization import check_url_canonicalization

# Initialize an error log
error_log = []

def log_error(message):
    """A simple function to log errors for later use."""
    global error_log
    error_log.append(message)
    print(message)  # This will also print the error in the console

# Read websites from external file
with open('websites.txt', 'r') as f:
    websites = [line.strip() for line in f.readlines()]

# Initialize Markdown report
report_md = "# Websites Monitor\n"

# Read the project description and usage instructions
with open('project_description.md', 'r') as f:
    report_md += f"{f.read()}\n"

with open('usage_instructions.md', 'r') as f:
    report_md += f"{f.read()}\n"

# Initialize the table
report_md += "\n## Monitoring Checks\n"
report_md += "[![Create report](https://github.com/fabriziosalmi/websites-monitor/actions/workflows/create-report.yml/badge.svg)](https://github.com/fabriziosalmi/websites-monitor/actions/workflows/create-report.yml)\n"
report_md += "| Check Type | " + " | ".join(websites) + " |\n"
report_md += "|------------|" + "---|" * len(websites) + "\n"

# List of check functions and their human-readable names
check_functions = [
    ("Domain breach", check_domain_breach),
    ("Domain Expiration", check_domain_expiration),
    ("SSL Expiration", check_ssl_cert),
    ("DNS Blacklists (Spamhaus + Spamcop)", check_dns_blacklist),
    ("DNS Blacklist (DomainsBlacklists)", check_domainsblacklists_blacklist),
    ("Headers", check_security_headers),
    ("HSTS", check_hsts),
    ("XSS Protection", check_xss_protection),
    ("Redirect chains", check_redirect_chains),
    ("Pagespeed Performances", check_pagespeed_performances),
    ("Website Load Time", check_website_load_time),
    ("Rate limited", check_rate_limiting),
    ("CDN", check_cdn),
    ("Brotli", check_brotli_compression),
    ("Deprecated libs", check_deprecated_libraries),
    ("Client rendering", check_clientside_rendering),
    ("Mixed content", check_mixed_content),
    ("Content-Type headers", check_content_type_headers),
    ("Internationalization", check_internationalization),
    ("FLOC", check_floc),
    ("AMP", check_amp_compatibility),
    ("Robots.txt", check_robot_txt),
    ("Sitemap", check_sitemap),
    ("Favicon", check_favicon),
    ("Alt Tags", check_alt_tags),
    ("Open Graph Protocol", check_open_graph_protocol),
    ("Semantic Markup", check_semantic_markup),
    ("Ad and tracking", check_ad_and_tracking),
    ("Privacy-Protected Whois", check_privacy_protected_whois),
    ("Privacy Exposure", check_privacy_exposure),
# testing..
#     ("Mobile friendly", check_mobile_friendly),
#     ("SSL cyphers", check_ssl_cipher_strength),
#     ("Browser compatibility", check_browser_compatibility),
#     ("DNSSEC", check_dnssec),
#     ("External links", check_external_links),
#    ("Subdomain Enumeration", check_subdomain_enumeration),
#     ("Minifications", check_asset_minification),
#     ("Broken links", check_broken_links),
#     ("Response time", check_server_response_time),
#     ("Subresources integrity", check_subresource_integrity),
#     ("3rd party requests", check_third_party_requests),
#     ("3rd party resources", check_third_party_resources),
#     ("URL canonicalization", check_url_canonicalization),
#     ("CORS Headers", check_cors_headers),
#     ("Cookie flags", check_cookie_flags),
#     ("Cookie policy", check_cookie_policy),
#     ("Cookie duration", check_cookie_duration),
#     ("Cookie Same-Site", check_cookie_samesite_attribute),
]

# Populate the table with check results
for check_name, check_func in check_functions:
    report_md += f"| {check_name} | "
    for website in websites:
        try:
            result = check_func(website)
            report_md += f"{result} | "
        except Exception as e:
            err_msg = f"Error occurred with {check_name} for {website}: {e}"
            log_error(err_msg)
            report_md += "⚪ | "  # Add a default grey indicator for errors
    report_md += "\n"

# Timestamp
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
report_md += f"\n---\nLast Updated: {current_time}\n"

# Write the Markdown report to a file
with open("README.md", "w") as f:
    f.write(report_md)

# Exit with a non-zero code if errors were encountered
if error_log:
    exit(1)
