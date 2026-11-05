# Changelog

All notable changes to Website Monitor are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.1] - 2026-11-05

### Fixed
- Web UI: no empty gap above the summary on the Results view when no scan is running; the status filter no longer sticks out of its panel on narrow screens; a long domain among the recent targets is shortened with an ellipsis instead of overflowing its chip; hyphens in table cells keep their normal width ("X-Frame-Options").
- README: a single check from the web UI (Run again) is a `scan` with one check, not `run_check`; the screenshots show the 2.0.0 API. The page description mentions the command line and the MCP server.

### Added
- `tests/test_docs.py`: the README must cite every endpoint, command, MCP tool and environment variable that exists, and none that does not.

## [2.0.0] - 2026-11-05

The REST API, a new command line and a new MCP server share one implementation and return the same JSON. Some responses change: see Changed.

### Added
- A command line, `python -m websites_monitor` (`websites-monitor` in the Docker image), with the commands health, checks, check, scan, scan-many, report, serve and mcp. `--json` prints the JSON the REST API returns; `--fail-on fail|warn` sets exit code 1 for CI.
- An MCP server for AI assistants over stdio or streamable HTTP, with one tool per operation and the same JSON as the REST API.
- Every check result carries `verdict` (pass, warn, fail, unknown), `detail`, `category` and `duration_ms`; scans carry a `summary` with the counts and the pass rate.
- `concurrency` on the scan requests, and `category` on `GET /checks`.
- The web UI's JSON export is the `scan` response of the API.

### Changed
- The code is laid out as ports and adapters in the `websites_monitor` package: one `MonitorService` implements every operation, and the REST API, the command line and the MCP server only translate to it. `api.py` and `main.py` remain as entry points.
- One registry of checks replaces the two that disagreed. As a result `check_name` holds the check's name ("SSL certificate", not "Ssl Cert"), the scheduled report's columns use the same names, the scheduler sends 10 requests in the rate limiting check like the API, and the API applies the longer minimum timeouts of the PageSpeed (60 s) and DNS blocklist (45 s) checks.
- Timestamps are UTC with an offset (`2026-11-05T11:36:23+00:00`).
- `GET /monitor/single` returns the same response as `POST /monitor/single`, not the grouped response of `POST /monitor`.
- `GET /check/{id}` answers 200 with `status: error` when the check fails or times out, as the other endpoints do, instead of 500.
- `POST /monitor` and the reports run checks concurrently (4 at a time by default) instead of one by one.
- The Markdown report starts each row with a pipe, and `POST /generate-report` renders it in memory instead of writing `api_generated_report.md`.

### Fixed
- The HTML report put the scanned site's results into the page unescaped.

## [1.5.0] - 2026-11-05

### Added
- The web UI is available in Italian. By default it follows the browser's language, and Settings can fix it to English or Italian. Numbers and dates follow the language; the text the checks return stays in English.

### Fixed
- Dates inside a sentence are no longer capitalised ("started today 10:47").
- The container image link in Settings points to ghcr.io instead of the outdated Docker Hub image.

## [1.4.1] - 2026-11-05

### Fixed
- The API reference (`docs/swagger.html` and `/api/docs`) renders: the vendored Swagger UI 4.15.5 could not read the OpenAPI 3.1 description FastAPI emits. It is replaced by Swagger UI 5.34.0, served with a versioned URL so browsers do not keep the cached copy.
- `/api/docs` no longer loads Swagger UI from cdn.jsdelivr.net.
- `docs/security.txt` declares the same canonical location as `docs/.well-known/security.txt`.

### Changed
- The GitHub Pages actions move to their current major versions, and the site keeps publishing `.well-known/security.txt`.
- Dependabot no longer proposes new Python minor or major versions for the base image; patch digests still come through.

## [1.4.0] - 2026-11-05

### Added
- Web UI rewritten on the design system shared with secure-proxy-manager and rustcd. Each check runs as its own request, four at a time, with live progress, per-check retry, filters, CSV and JSON export, scan history, a check catalog, settings, light and dark themes and a mobile layout.
- CI: tests on Python 3.11, and an image smoke test under the 256 MB memory limit.
- Image workflow: linux/amd64 and linux/arm64 images on ghcr.io, with provenance and an SBOM.
- Dependabot for pip, the base image and the GitHub Actions.
- `docs/openapi.json`, a snapshot of the API description for the API reference on GitHub Pages, kept in step with the code by a test, and `SECURITY.md`.
- `GITHUB_TOKEN`, `WAVE_API_KEY`, `WM_BIND_ADDRESS`, `WM_PORT`, `OUTPUT_FILE`, `API_RELOAD` and `WM_CACHE_DIR` settings.

### Changed
- `POST /monitor/single` runs each requested check once and returns its `check_id`; asking for five checks used to run nine.
- `GET /checks` lists the 53 checks once each, in seven categories, instead of 63 entries mostly filed under "other".
- `website` is reduced to its host in every endpoint.
- The report is written to `report.md` (`reports/report.md` in Docker) instead of `README.md`, and no longer starts with `usage.md`.
- Docker Compose publishes the API on 127.0.0.1:8000 unless `.env` sets another address and port.
- A check that cannot run returns no verdict with the reason, for example `(no PageSpeed API key)`.
- `pagespeed_performances` maps its score onto Lighthouse's bands instead of returning a bare number.
- Dependencies and the base image are pinned.

### Fixed
- The API ran out of memory and was killed during scans: the domain blacklist (5.5 million lines) was loaded into a set that took 916 MB. It is now read from disk with flat memory.
- uvicorn ran with auto reload in production and dropped requests whenever a file changed.
- Checks blocked the API's event loop, `/health` included.
- `dns_blacklist` read Spamhaus error codes as listings and reported every domain as listed.
- `cms_used` reported Magento for pages with a PNG favicon and WordPress for github.com.
- `domain_expiration`, `dnssec`, `email_domain`, `accessibility`, `mobile_friendly`, `data_leakage`, `browser_compatibility`, `external_links`, `subresource_integrity` and `subdomain_enumeration`, and the five checks that needed lxml.
- `main.py` exited 0 after a failure, and the scheduled GitHub Action could not fail.
- `GET /` served the web UI without its stylesheet, scripts and fonts.
- Results from the scanned site were inserted into the page as HTML.

### Removed
- The `production` Compose profile: it required `docker/nginx.conf` and `docker/init.sql`, which did not exist, and no code used Redis or PostgreSQL.
- `usage.md`, `project_description.md` and `debug_scheduler.py`.

## [1.3.0] - 2025-06-02

### Added
- FastAPI web interface with interactive UI
- REST API with 53+ security, performance, and compliance checks
- Docker and Docker Compose support
- Comprehensive check categories:
  - Security & Protection (10 checks)
  - Performance & Speed (8 checks)
  - SEO & Content (9 checks)
  - Domain & DNS (7 checks)
  - Privacy & Tracking (10 checks)
  - Accessibility & Mobile (5 checks)
  - Technical & Infrastructure (4 checks)

### Changed
- Migrated from basic script to full FastAPI application
- Improved error handling and logging
- Enhanced check organization by category

## [1.0.0] - 2025-03-22

### Added
- Basic website monitoring functionality
- GitHub Actions integration for automated daily checks
- Markdown report generation
- Core security and performance checks

[Unreleased]: https://github.com/fabriziosalmi/websites-monitor/compare/v2.0.1...HEAD
[2.0.1]: https://github.com/fabriziosalmi/websites-monitor/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/fabriziosalmi/websites-monitor/compare/v1.5.0...v2.0.0
[1.5.0]: https://github.com/fabriziosalmi/websites-monitor/compare/v1.4.1...v1.5.0
[1.4.1]: https://github.com/fabriziosalmi/websites-monitor/compare/v1.4.0...v1.4.1
[1.4.0]: https://github.com/fabriziosalmi/websites-monitor/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/fabriziosalmi/websites-monitor/compare/v1.2.0...v1.3.0
[1.0.0]: https://github.com/fabriziosalmi/websites-monitor/releases/tag/v1.0.0
