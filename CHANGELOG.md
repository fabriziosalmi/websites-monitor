# Changelog

All notable changes to the Website Monitor project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive CONTRIBUTING.md with development guidelines
- MIT LICENSE file
- Detailed troubleshooting section in README
- Project structure documentation
- FAQ section answering common questions
- Quick Links navigation in README
- Badges for license, Python version, and Docker
- Comprehensive API usage examples with multiple scenarios
- Detailed check categories reference table
- Enhanced status indicators documentation

### Changed
- Improved GitHub Actions setup instructions with step-by-step guide
- Enhanced .env.example with better organization and comments
- Updated project_description.md with architecture details
- Expanded usage.md with better structure
- Improved DOCKER.md with corrected API paths

### Fixed
- Corrected API endpoint from POST /check to POST /monitor
- Fixed API documentation paths from /docs to /api/docs
- Fixed output_file default in documentation (report.md, not README.md)
- Updated config.yaml to include all documented options
- Corrected documentation paths throughout

## [1.3.0] - 2024

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

## [1.0.0] - Initial Release

### Added
- Basic website monitoring functionality
- GitHub Actions integration for automated daily checks
- Markdown report generation
- Core security and performance checks

---

## Version History

- **1.3.0**: Current version with full API and web interface
- **1.0.0**: Initial release with basic monitoring

[Unreleased]: https://github.com/fabriziosalmi/websites-monitor/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/fabriziosalmi/websites-monitor/releases/tag/v1.3.0
[1.0.0]: https://github.com/fabriziosalmi/websites-monitor/releases/tag/v1.0.0
