# Websites Monitor
## Project Description
This project aims to continuously monitor various aspects of specified websites. It checks performances, security headers, SSL/TLS certificates, domain expiration, and CDN enablement. The GitHub action is scheduled to run once a day and updates this README with the latest results.

## How to Use
1. Fork this repository.
2. Add the websites you want to monitor in the `websites.txt` file, one per line.
3. Enable GitHub Actions if not already enabled.
4. The README will be automatically updated with the latest check results once a day.

### Monitoring Checks
| Site | Performances | CSP | Headers | SSL | Expiration | CDN |
|------|-----------------|--------------------------|------------------|-----|--------|-----|
| audiolibri.org | 99.0 | CSP | Revealing-Headers | 🟢 | 🟢 | 🟠 |
| get.domainsblacklists.com | 99.0 | CSP | Revealing-Headers | 🟢 | 🟢 | 🟠 |

---
Last Updated: 2023-09-05 22:09:34