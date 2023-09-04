import requests
import json
from datetime import datetime

# List of websites to test
websites = [
    'https://audiolibri.org',
    'https://get.domainsblacklists.com'
]

# Initialize Markdown report with table header
report_md = "# Websites\n## PageSpeed and Security Header Report\n| Site | PageSpeed Score | Content-Security-Policy |\n|------|-----------------|--------------------------|\n"

for website in websites:
    # PageSpeed API
    pagespeed_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={website}"
    pagespeed_response = requests.get(pagespeed_url)
    pagespeed_data = json.loads(pagespeed_response.text)
    pagespeed_score = pagespeed_data["lighthouseResult"]["categories"]["performance"]["score"] * 100

    # Security Headers Check
    security_response = requests.get(website)
    csp_header = security_response.headers.get('Content-Security-Policy', 'Not Set')

    # Update Markdown report with table row data
    report_md += f"| {website} | {pagespeed_score} | {csp_header} |\n"

# Get the current time and format it as a string
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Add a "Last Updated" timestamp to the Markdown report
report_md += f"\n---\nLast Updated: {current_time}"

# Save report to a Markdown file
with open("README.md", "w") as f:
    f.write(report_md)
