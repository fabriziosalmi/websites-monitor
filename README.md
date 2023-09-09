# Websites Monitor
## Project Description

This project aims to continuously monitor various aspects of specified websites. It runs a variety of checks, ranging from performance to security considerations. The GitHub Action is scheduled to run once per day, updating this README with the latest results.

_This project is in super mega ultra alpha status.. double check and review everything before to clone and use it :)_

## How to Use

1. Fork this repository.
2. Add the websites you want to monitor in the `websites.txt` file, one per line.
3. Enable GitHub Actions if not already enabled.
4. The README will be automatically updated with the latest check results once a day.


## Monitoring Checks
[![Create report](https://github.com/fabriziosalmi/websites-monitor/actions/workflows/create-report.yml/badge.svg)](https://github.com/fabriziosalmi/websites-monitor/actions/workflows/create-report.yml)
| Check Type | audiolibri.org | get.domainsblacklists.com | example.com |
|------------|---|---|---|
| Pagespeed Performances | 94 | 99 | 100 | 
| Headers | 🔴 | 🔴 | 🔴 | 
| SSL Expiration | 🟢 | 🟢 | 🟢 | 
| SSL cyphers | ⚪ | ⚪ | ⚪ | 
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
| Subdomain Enumeration | ('🟢', []) | ('🟢', []) | ('🔴', ['www']) | 
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
| Response time | ⚪ | ⚪ | ⚪ | 
| Subresources integrity | ('🔴', 0) | ('🔴', 0) | ('🔴', 0) | 
| 3rd party resources | ⚪ | ⚪ | ⚪ | 

---
Last Updated: 2023-09-09 04:03:47
