# Website Monitor

[![CI](https://github.com/fabriziosalmi/websites-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/fabriziosalmi/websites-monitor/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Website Monitor runs 53 checks against a website: TLS, security headers, performance, SEO, DNS, privacy and accessibility. It has a web UI, a REST API, and a scheduler that writes a Markdown report for a list of sites.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/screenshot-dark.png">
  <img alt="Results of a scan of example.com in the web UI: pass rate, failed checks, warnings, a breakdown per category and the list of checks" src="docs/screenshot.png">
</picture>

## Contents

- [Quick start](#quick-start)
- [Web UI](#web-ui)
- [Verdicts](#verdicts)
- [Checks](#checks)
- [REST API](#rest-api)
- [Scheduled reports](#scheduled-reports)
- [Configuration](#configuration)
- [Development](#development)

## Quick start

With Docker Compose:

```bash
git clone https://github.com/fabriziosalmi/websites-monitor.git
cd websites-monitor
cp .env.example .env        # optional keys, address and port
docker compose up -d --build
```

Open http://127.0.0.1:8000/ for the web UI. The API answers on the same port; its interactive reference is at http://127.0.0.1:8000/api/docs.

Compose starts two containers, each limited to 256 MB of memory:

- `website-monitor-api`: the REST API and the web UI.
- `website-monitor-scheduler`: runs every check against the sites in `config.yaml` every `MONITOR_INTERVAL` seconds and writes `reports/report.md`.

By default the port is published on 127.0.0.1 only. To reach it from other machines, set `WM_BIND_ADDRESS` (an address of the host, or `0.0.0.0`) and `WM_PORT` in `.env`.

The API has no authentication, and its checks send requests to whatever host they are given, including hosts on your internal network. Publish it only on a trusted network or behind an authenticating reverse proxy; see [SECURITY.md](SECURITY.md).

Without Docker, with Python 3.11:

```bash
pip install -r requirements.txt
python api.py               # API and web UI on http://127.0.0.1:8000/
python main.py              # one run over config.yaml, writes report.md
```

## Web UI

The web UI is a static page in `docs/`, served by the API under `/docs/` (`/` redirects there).

- **New scan**: a domain or URL (only the host is used) and the checks to run, all 53 by default.
- **Results**: each check runs as its own request, four at a time, so results appear as they finish. The page shows the pass rate, the number of failed checks, warnings and checks without a verdict, a breakdown per category, and the list of checks with filters and search. A single check can be run again, and the `curl` command for it copied. Results export to CSV and JSON.
- **History**: the last 20 scans, kept in the browser's local storage.
- **Check catalog**: every check with its ID, category and description.
- **Settings**: the API address, the timeout per check, how many checks run in parallel, an optional PageSpeed key (kept in memory for the current tab only), and the theme (light, dark or system).

The same page is published on GitHub Pages at https://fabriziosalmi.github.io/websites-monitor/. There it has no API behind it: set the address of a running API in Settings. A page served over HTTPS can only call an API served over HTTPS.

## Verdicts

Every check returns a verdict, sometimes followed by a detail in parentheses, such as `(50 days left)`. The API returns the verdict as a coloured circle at the start of the `result` string:

| Symbol | Verdict | Meaning |
|---|---|---|
| U+1F7E2 green circle | Pass | The site meets the check. |
| U+1F7E1 yellow circle, U+1F7E0 orange circle | Warning | Partly met, or worth a look. |
| U+1F534 red circle | Fail | The site does not meet the check. |
| U+26AA white circle | No verdict | The check could not decide: an error, a timeout, a missing API key, or nothing to check. The detail says why when the check knows, for example `(no PageSpeed API key)`. |

The pass rate in the web UI is the share of passed checks among those with a verdict; checks without a verdict are left out.

## Checks

Some checks need a key to give a verdict; without it they return no verdict and name the key:

- `pagespeed_performances` needs `PAGESPEED_API_KEY`. The score is mapped onto Lighthouse's bands: 90 to 100 pass, 50 to 89 warning, 0 to 49 fail.
- `data_leakage` needs `GITHUB_TOKEN` (GitHub code search requires authentication).
- `accessibility` uses Lighthouse through the PageSpeed API, then the WAVE API if `WAVE_API_KEY` is set, and otherwise its own heuristics on the page HTML; a heuristic result is marked `(heuristic)`.
- `browser_compatibility` loads the page in Chrome and Firefox through Selenium. The Docker image ships no browser, so there it returns `(no browser available)`.
- `dns_blacklist` checks the IPv4 address the domain resolves to. Behind a CDN that is the CDN's address.

<details>
<summary>All 53 checks</summary>

**Security** (10)

| Check | ID | What it looks at |
|---|---|---|
| SSL certificate | `ssl_cert` | Validity and days to expiry |
| TLS cipher strength | `ssl_cipher_strength` | Negotiated cipher suite |
| Security headers | `security_headers` | CSP, X-Frame-Options and others |
| HSTS | `hsts` | Strict-Transport-Security header |
| XSS protection | `xss_protection` | X-XSS-Protection header |
| CORS policy | `cors_headers` | Cross-origin response headers |
| Mixed content | `mixed_content` | HTTP resources on HTTPS pages |
| Subresource integrity | `subresource_integrity` | SRI on external scripts and styles |
| Rate limiting | `rate_limiting` | Response to a burst of requests |
| Data leakage | `data_leakage` | Mentions in public GitHub code |

**Performance** (8)

| Check | ID | What it looks at |
|---|---|---|
| PageSpeed score | `pagespeed_performances` | Google PageSpeed Insights |
| Load time | `website_load_time` | Total time to load the page |
| Server response time | `server_response_time` | Time to first byte |
| Brotli compression | `brotli_compression` | Content-Encoding: br |
| Asset minification | `asset_minification` | CSS and JavaScript minified |
| CDN | `cdn` | Content delivery network in front |
| Redirect chains | `redirect_chains` | Number of hops to the final URL |
| HTTPS redirect | `redirects` | HTTP redirects to HTTPS |

**SEO and content** (9)

| Check | ID | What it looks at |
|---|---|---|
| Sitemap | `sitemap` | sitemap.xml present and valid |
| robots.txt | `robot_txt` | Present and well formed |
| Open Graph tags | `open_graph_protocol` | Social sharing metadata |
| Image alt text | `alt_tags` | Every image has an alt attribute |
| Semantic markup | `semantic_markup` | Structured data in the page |
| Canonical URL | `url_canonicalization` | rel="canonical" link |
| Favicon | `favicon` | Site icon present |
| Broken links | `broken_links` | Internal links that fail |
| External links | `external_links` | Outbound links reachable |

**Domain and DNS** (7)

| Check | ID | What it looks at |
|---|---|---|
| Domain expiration | `domain_expiration` | Registration expiry date |
| DNSSEC | `dnssec` | Signed DNS zone |
| DNS blocklists | `dns_blacklist` | Listed on DNS-based blocklists |
| Breach exposure | `domain_breach` | Domain in known data breaches |
| Domain blocklists | `domainsblacklists_blacklist` | Aggregated threat lists |
| Subdomains | `subdomain_enumeration` | Common subdomains that resolve |
| Email records | `email_domain` | SPF and mail records |

**Privacy and tracking** (10)

| Check | ID | What it looks at |
|---|---|---|
| Cookie policy | `cookie_policy` | Policy page linked |
| Cookie flags | `cookie_flags` | Secure and HttpOnly set |
| Cookie duration | `cookie_duration` | Session cookie lifetimes |
| Cookie SameSite | `cookie_samesite_attribute` | SameSite attribute set |
| Ads and tracking | `ad_and_tracking` | Analytics and ad scripts |
| FLoC opt-out | `floc` | interest-cohort permission policy |
| Privacy exposure | `privacy_exposure` | Sensitive data in the page |
| WHOIS privacy | `privacy_protected_whois` | Registrant data redacted |
| Third-party requests | `third_party_requests` | Requests to other domains |
| Third-party resources | `third_party_resources` | Scripts and styles from other domains |

**Accessibility and mobile** (5)

| Check | ID | What it looks at |
|---|---|---|
| Accessibility | `accessibility` | Accessibility score |
| Mobile friendly | `mobile_friendly` | Viewport and responsive layout |
| AMP | `amp_compatibility` | AMP version available |
| Internationalization | `internationalization` | lang and hreflang attributes |
| Browser compatibility | `browser_compatibility` | Markup older browsers handle |

**Technical** (4)

| Check | ID | What it looks at |
|---|---|---|
| Content-Type header | `content_type_headers` | MIME type and charset |
| CMS detection | `cms_used` | Platform behind the site |
| Client-side rendering | `clientside_rendering` | Content rendered by JavaScript |
| Deprecated libraries | `deprecated_libraries` | Outdated JavaScript libraries |

</details>

## REST API

The API is a FastAPI application (`api.py`). `website` accepts a domain or a URL; only the host is used. The interactive reference is served at `/api/docs` (Swagger UI) and `/api/redoc`, and the OpenAPI description at `/api/openapi.json`.

| Method and path | What it does |
|---|---|
| `GET /health` | Status, version and number of checks. |
| `GET /checks` | The 53 checks: ID, category, description and endpoint. |
| `POST /monitor/single` | Runs the listed checks against one website. Each check runs once, in the order given. |
| `GET /monitor/single?website=` | Runs every check against one website. |
| `GET /check/{id}?website=` | Runs one check. |
| `POST /monitor` | Runs every check against a list of websites and waits for the results. |
| `POST /monitor/async` | Same, in the background: returns a task ID. |
| `GET /monitor/async/{task_id}` | Status and result of a background task. Tasks live in memory and are lost on restart. |
| `POST /generate-report` | Runs every check and returns a report as JSON, Markdown or HTML (`output_format`). |

Run three checks against one site:

```bash
curl -s -X POST http://127.0.0.1:8000/monitor/single \
  -H 'Content-Type: application/json' \
  -d '{"website": "example.com", "checks": ["ssl_cert", "hsts", "pagespeed_performances"]}'
```

```json
{
  "success": true,
  "message": "Custom monitoring completed successfully",
  "results": [
    {
      "check_id": "ssl_cert",
      "check_name": "Ssl Cert",
      "website": "example.com",
      "result": "\ud83d\udfe2 (50 days left)",
      "status": "completed",
      "timestamp": "2026-11-05T10:56:44.284830"
    },
    {
      "check_id": "hsts",
      "check_name": "Hsts",
      "website": "example.com",
      "result": "\ud83d\udd34",
      "status": "completed",
      "timestamp": "2026-11-05T10:56:44.351761"
    },
    {
      "check_id": "pagespeed_performances",
      "check_name": "Pagespeed Performances",
      "website": "example.com",
      "result": "\u26aa (no PageSpeed API key)",
      "status": "completed",
      "timestamp": "2026-11-05T10:56:44.351920"
    }
  ],
  "execution_time": 0.172866,
  "timestamp": "2026-11-05T10:56:44.351921",
  "websites_checked": 1,
  "checks_performed": 3
}
```

`result` starts with the verdict (shown here as JSON escapes; see [Verdicts](#verdicts)). When a check raises an error or exceeds its timeout, `status` is `error`, `result` is the white circle and `error` holds the message, for example `Timed out after 30s`. An unknown check ID comes back with `"error": "Unknown check"`.

`timeout` (5 to 300 seconds, default 30) limits each check, and `pagespeed_api_key` overrides `PAGESPEED_API_KEY` for one request. Both are optional fields of the request body.

## Scheduled reports

`main.py` runs every check against the `websites` in `config.yaml` and writes a Markdown table, one row per site, to `output_file`. It exits with status 1 when it cannot produce the report.

- **Docker**: the scheduler container runs `main.py` every `MONITOR_INTERVAL` seconds and writes `reports/report.md`.
- **GitHub Actions**: `.github/workflows/create-report.yml` runs `main.py` daily at 04:00 UTC and commits `report.md`. GitHub disables scheduled workflows in repositories without recent activity; enable it from the Actions tab of your fork. Set the `PAGESPEED_API_KEY` repository secret for the PageSpeed check.

## Configuration

`config.yaml`, read by `main.py` and the scheduler:

| Key | Default | Meaning |
|---|---|---|
| `websites` | | Domains or URLs to check. |
| `timeout` | `30` | Seconds each check may take. |
| `output_file` | `report.md` | Where the report is written. The `OUTPUT_FILE` variable overrides it. |
| `report_template` | `report_template.md` | Optional text placed above the table. |

Environment variables (see `.env.example`):

| Variable | Used by | Meaning |
|---|---|---|
| `WM_BIND_ADDRESS`, `WM_PORT` | Docker Compose | Address and port where the API is published. Default `127.0.0.1` and `8000`. |
| `PAGESPEED_API_KEY` | `pagespeed_performances`, `accessibility` | Google PageSpeed Insights API key. |
| `GITHUB_TOKEN` | `data_leakage` | GitHub token for code search. |
| `WAVE_API_KEY` | `accessibility` | WAVE API key. |
| `MONITOR_INTERVAL` | scheduler | Seconds between two runs. Default 3600. |
| `OUTPUT_FILE` | `main.py` | Report path, overriding `config.yaml`. |
| `API_HOST`, `API_PORT` | `python api.py` | Listen address and port. Default `0.0.0.0` and `8000`. |
| `API_RELOAD` | `python api.py` | `1` restarts the server on code changes. Development only: a restart drops requests in progress. |
| `WM_CACHE_DIR` | `domainsblacklists_blacklist` | Where the 107 MB domain blacklist is cached. Default: a `websites-monitor` directory in the system temp directory. |

## Container image

Each push to `main` publishes `ghcr.io/fabriziosalmi/websites-monitor` for linux/amd64 and linux/arm64, with provenance and an SBOM; tags `v*` add version tags. `docker compose` builds the image locally from the `Dockerfile`.

## Development

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

The tests do not use the network. CI runs them on Python 3.11, then builds the image, starts it with a 256 MB memory limit and calls the API.

To add a check:

1. Write `checks/check_<id>.py` with a function `check_<id>(website: str) -> str` that returns a verdict as described in [Verdicts](#verdicts), and never raises.
2. Register it in `CHECK_MODULES` and `CHECK_CATEGORIES` in `api.py`, and in `WebsiteMonitor._initialize_check_functions` in `main.py` for the scheduled report.
3. Add it to `CHECKS` in `docs/assets/app.js`. A test fails while the web UI and the API disagree on the list or the categories.
4. Run `python scripts/export_openapi.py` to refresh `docs/openapi.json`, which the API reference on GitHub Pages loads. A test fails when it is out of date.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the rest, and [SECURITY.md](SECURITY.md) to report a vulnerability.

## License

MIT, see [LICENSE](LICENSE).
