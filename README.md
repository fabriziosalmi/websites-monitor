# Websites Monitor
## Project Description

This project aims to continuously monitor various aspects of specified websites. It runs a variety of checks, ranging from performance to security considerations. The GitHub Action is scheduled to run once per day, updating this README with the latest results.

![Static Badge](https://img.shields.io/badge/project_status-alpha-red?style=for-the-badge&logo=github)

## How to Use

1. Fork this repository.
2. Add the websites you want to monitor in the `websites.txt` file, one per line.
3. Enable GitHub Actions if not already enabled.
4. The README will be automatically updated with the latest check results once a day.


## Monitoring Checks
[![Create report](https://github.com/fabriziosalmi/websites-monitor/actions/workflows/create-report.yml/badge.svg)](https://github.com/fabriziosalmi/websites-monitor/actions/workflows/create-report.yml)
| Check Type | audiolibri.org | get.domainsblacklists.com | example.com |
|------------|---|---|---|
| Domain breach | 🔘 | 🔘 | 🔘 | 
| Domain Expiration | 🟢 (218 days left) | 🟢 (306 days left) | 🟢 (320 days left) | 
| SSL Expiration | 🟢 (56 days left) | 🟢 (89 days left) | 🟢 (139 days left) | 
| DNS Blacklists (Spamhaus + Spamcop) | 🟢 | 🟢 | 🟢 | 
| DNS Blacklist (DomainsBlacklists) | 🟢 | 🟢 | 🟢 | 
| HSTS | 🟢 | 🟢 | 🔴 | 
| XSS Protection | 🟢 | ⚪ | 🔴 | 
| Redirect chains | 🟢 | 🟢 | 🟢 | 
| Pagespeed Performances | 99 | 99 | 100 | 
| Website Load Time | 🟢 | 🟢 | 🟢 | 
| Rate limited | 🔴 | 🔴 | 🔴 | 
| CDN | 🔴 | 🔴 | 🔴 | 
| Brotli | 🟢 | 🟢 | 🔴 | 
| Deprecated libs | 🟢 | 🟢 | 🟢 | 
| Client rendering | 🔴 | 🟢 | 🟢 | 
| Mixed content | 🔴 | 🟢 | 🟢 | 
| Content-Type headers | 🟢 | 🟢 | 🟢 | 
| Internationalization | ⚪ | ⚪ | ⚪ | 
| FLOC | 🔴 | 🟢 | 🔴 | 
| AMP | 🔴 | 🔴 | 🔴 | 
| Robots.txt | 🔴 | 🔴 | 🔴 | 
| Sitemap | 🔴 | 🔴 | 🔴 | 
| Favicon | 🟢 | 🔴 | 🔴 | 
| Alt Tags | 🟢 | 🔴 | 🔴 | 
| Open Graph Protocol | 🟢 | 🟢 | 🟢 | 
| Semantic Markup | 🔴 | 🔴 | 🔴 | 
| Ad and tracking | 🟢 | 🟢 | 🟢 | 
| Privacy-Protected Whois | 🔴 | 🔴 | 🔴 | 
| Privacy Exposure | 🔴 | 🟢 | 🟢 | 

---
Last Updated: 2023-09-27 04:03:52
