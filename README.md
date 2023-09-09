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
| Pagespeed Performances | 98 | 99 | 100 | 
| Headers | 🔴 | 🔴 | 🔴 | 
| SSL Expiration | 🟢 | 🟢 | 🟢 | 
| Domain Expiration | 🟢 | 🟢 | 🟢 | 
| CDN | 🔴 | 🔴 | 🔴 | 
| DNS Blacklists (Spamhaus + Spamcop) | 🟢 | 🟢 | 🟢 | 
| DNS Blacklist (DomainsBlacklists) | 🟢 | 🟢 | 🟢 | 
| Alt Tags | 🟢 | 🔴 | 🔴 | 
| HSTS | 🟢 | 🟢 | 🔴 | 
| Open Graph Protocol | 🟢 | 🟢 | 🟢 | 
| Privacy-Protected Whois | 🔴 | 🔴 | 🔴 | 
| Privacy Exposure | 🔴 | 🟢 | 🟢 | 
| Robots.txt | 🔴 | 🔴 | 🔴 | 
| Sitemap | 🔴 | 🔴 | 🔴 | 
| Semantic Markup | 🔴 | 🔴 | 🔴 | 
| Website Load Time | 🟢 | 🟢 | 🟢 | 
| XSS Protection | 🟢 | ⚪ | 🔴 | 
| Domain breach | 🔘 | 🔘 | 🔘 | 
| Ad and tracking | 🟢 | 🟢 | 🟢 | 
| AMP | 🔴 | 🔴 | 🔴 | 
| Brotli | 🟢 | 🟢 | 🔴 | 
| Client rendering | 🔴 | 🟢 | 🟢 | 
| Content-Type headers | 🟢 | 🟢 | 🟢 | 
| Deprecated libs | 🟢 | 🟢 | 🟢 | 
| Favicon | 🟢 | 🔴 | 🔴 | 
| FLOC | 🔴 | 🟢 | 🔴 | 
| Internationalization | ⚪ | ⚪ | ⚪ | 
| Mixed content | 🔴 | 🟢 | 🟢 | 
| Rate limited | 🔴 | 🔴 | 🔴 | 
| Redirect chains | 🟢 | 🟢 | 🟢 | 

---
Last Updated: 2023-09-09 18:08:07
