# Websites Monitor
## Project Description

This project aims to continuously monitor various aspects of specified websites. It runs a variety of checks, ranging from performance to security considerations. The GitHub Action is scheduled to run once per day, updating this README with the latest results.

_This project is in super mega ultra alpha status.. double check and review everything before to clone and use it :)_

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
| Ad and tracking | 🟢 | 🟢 | 🟢 | 
| AMP | 🔴 | 🔴 | 🔴 | 
| Minifications | ⚪ | ⚪ | ⚪ | 
| Broken links | 🔴 | 🟢 | 🟢 | 
| Brotli | 🔴 | 🔴 | 🔴 | 
| Client rendering | 🔴 | 🟢 | 🟢 | 
| Content-Type headers | 🟢 | 🟢 | 🟢 | 
| Deprecated libs | 🟢 | 🟢 | 🟢 | 
| DNSSEC | 🔴 | 🔴 | 🔴 | 
| External links | 🟡 | 🟡 | 🟡 | 
| Favicon | 🔴 | 🔴 | 🔴 | 
| FLOC | 🔴 | 🔴 | 🔴 | 
| Internationalization | 🔴 | 🔴 | 🔴 | 
| Mixed content | 🟢 | 🟢 | 🟢 | 
| Mobile friendly | ⚪ | ⚪ | ⚪ | 
| Outdated JS | 🟢 | 🟢 | 🟢 | 
| Rate limited | 🔴 | 🔴 | 🔴 | 
| Redirect chains | 🟢 | 🟢 | 🟢 | 
| Response time | 🟡 | 🟡 | 🟡 | 
| Subresources integrity | 🔴 | 🔴 | 🔴 | 
| 3rd party requests | 🟡 | 🟡 | 🟡 | 
| 3rd party resources | ⚪ | ⚪ | ⚪ | 
| URL canonicalization | 🟢 | 🔴 | 🔴 | 

---
Last Updated: 2023-09-07 13:20:57
