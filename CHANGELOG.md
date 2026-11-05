# Changelog

All notable changes to Website Monitor are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.4.1] - 2026-11-05

### Fixed
- The API reference (`docs/swagger.html` and `/api/docs`) renders again: the vendored Swagger UI 4.15.5 could not read the OpenAPI 3.1 description FastAPI emits. It is replaced by Swagger UI 5.34.0, served with a versioned URL so browsers do not keep the cached copy.
- `/api/docs` no longer loads Swagger UI from cdn.jsdelivr.net.
- The scheduler container is no longer reported unhealthy: it inherited the image's health check, which probes the API port.
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

[Unreleased]: https://github.com/fabriziosalmi/websites-monitor/compare/v1.4.1...HEAD
[1.4.1]: https://github.com/fabriziosalmi/websites-monitor/compare/v1.4.0...v1.4.1
[1.4.0]: https://github.com/fabriziosalmi/websites-monitor/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/fabriziosalmi/websites-monitor/compare/v1.2.0...v1.3.0
[1.0.0]: https://github.com/fabriziosalmi/websites-monitor/releases/tag/v1.0.0
