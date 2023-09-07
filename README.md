# Websites Monitor
## Project Description
This project aims to continuously monitor various aspects of specified websites. It runs a variety of checks, ranging from performance to security considerations. The GitHub Action is scheduled to run once per day, updating this README with the latest results.

## How to Use
1. Fork this repository.
2. Add the websites you want to monitor in the `websites.txt` file, one per line.
3. Enable GitHub Actions if not already enabled.
4. The README will be automatically updated with the latest check results once a day.

### Monitoring Checks
| Check Type | audiolibri.org | get.domainsblacklists.com | example.com |
|------------|---|---|---|
| Pagespeed Performances | 99 | 98 | 100 | 
| Headers | 🟠 | 🟠 | 🔴 | 
| SSL Expiration | 🟢 | 🟢 | 🟢 | 
| SSL cyphers | ⚪ | ⚪ | ⚪ | 
| Domain Expiration | 🟢 | 🟢 | 🟢 | 
| CDN | 🟠 | 🟠 | 🟠 | 
| DNS Blacklists (Spamhaus + Spamcop) | 🟢 | 🟢 | 🟢 | 
| DNS Blacklist (DomainsBlacklists) | 🟢 | 🟢 | 🟢 | 
| Alt Tags | 🟢 | 🟢 | 🟢 | 
| CORS Headers | 🟢 | 🟢 | 🟢 | 
| Cookie flags | 🔴 | 🔴 | 🔴 | 
| Cookie policy | 🟠 | 🟠 | 🟠 | 
| Cookie duration | 🟡 | 🟡 | 🟡 | 
| Cookie Same-Site | ⚪ | ⚪ | ⚪ | 
| HSTS | 🟢 | 🔴 | 🔴 | 
| Open Graph Protocol | 🔴 | 🔴 | 🔴 | 
| Privacy-Protected Whois | 🔴 | 🔴 | 🔴 | 
| Privacy Exposure | 🔴 | 🔴 | 🟢 | 
| Robots.txt | 🔴 | 🔴 | 🔴 | 
| Sitemap | 🔴 | 🔴 | 🔴 | 
| Semantic Markup | 🔴 | 🔴 | 🔴 | 
| Subdomain Enumeration | 🟢 | 🟢 | 🔴 | 
| Website Load Time | 🟢 | 🟢 | 🟢 | 
| XSS Protection | 🟢 | 🟢 | 🔴 | 
| Domain breach | 🔘 | 🔘 | 🔘 | 

---
Last Updated: 2023-09-07 12:22:11
