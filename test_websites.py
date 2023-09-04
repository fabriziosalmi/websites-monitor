import requests
import json

# List of websites to test
websites = [
    'https://audiolibri.org',
    'https://get.domainsblacklists.com',
    'https://review.domainsblacklists.com'
]

# Initialize Markdown report with table header
report_md = "# Websites\n## PageSpeed performances report\n| Site | Score |\n|------|-------|\n"
text_md = f"\nTo add a new website to the monitoring workflow just add it to the test_websites.py file."

for website in websites:
    # PageSpeed API
    pagespeed_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={website}"
    pagespeed_response = requests.get(pagespeed_url)
    pagespeed_data = json.loads(pagespeed_response.text)
    pagespeed_score = pagespeed_data["lighthouseResult"]["categories"]["performance"]["score"] * 100

    # TODO: Add Lighthouse and Security Headers checks

    # Update Markdown report with table row data
    report_md += f"| {website} | {pagespeed_score} |\n"
    



# Save report to a Markdown file
with open("README.md", "w") as f:
    f.write(report_md)

# Save report to a Markdown file
with open("README.md", "w") as f:
    f.write(text_md)
