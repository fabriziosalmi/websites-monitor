# Website Monitor

[![GitHub Workflow Status](https://github.com/fabriziosalmi/websites-monitor/actions/workflows/create-report.yml/badge.svg)](https://github.com/fabriziosalmi/websites-monitor/actions/workflows/create-report.yml)

This repository provides a framework to monitor the health and security of your websites, automatically generating a detailed report in markdown format on a daily basis. It performs various checks, including domain status, SSL certificate validity, security headers, and performance metrics, helping you keep your online presence secure and optimized.

## Quick Start with Docker

The easiest way to get started is using the pre-built Docker image from Docker Hub:

```bash
# Pull and run the latest image
docker pull fabriziosalmi/website-monitor:latest
docker run -it fabriziosalmi/website-monitor:latest
```

### Docker Environment Variables

You can configure the tool using environment variables:

```bash
docker run -it \
  -e GOOGLE_API_KEY=your_google_api_key \
  -e GITHUB_TOKEN=your_github_token \
  fabriziosalmi/website-monitor:latest
```

### Docker with Configuration File

Mount your configuration file to customize settings:

```bash
docker run -it \
  -v /path/to/your/config.yaml:/app/config.yaml \
  fabriziosalmi/website-monitor:latest
```

## Features

The tool performs comprehensive website analysis including:

### Security Checks

-   **SSL/TLS Certificate validation** - Checks certificate validity, expiration, and configuration
-   **HSTS (HTTP Strict Transport Security)** - Verifies proper HSTS implementation
-   **Mixed Content Detection** - Identifies insecure HTTP resources on HTTPS sites
-   **CORS Headers Analysis** - Evaluates Cross-Origin Resource Sharing configuration
-   **Cookie Security** - Checks SameSite attributes and security flags
-   **FLoC Opt-out** - Verifies Google's Federated Learning of Cohorts opt-out

### Domain & DNS Checks

-   **Domain Expiration** - Monitors domain registration expiration dates
-   **DNSSEC Validation** - Checks DNS Security Extensions implementation
-   **DNS Blacklist Scanning** - Verifies domain against known malicious lists
-   **SPF Records** - Validates Sender Policy Framework for email security

### Content & Performance

-   **Mobile-Friendly Testing** - Uses Google's Mobile-Friendly Test API
-   **Favicon Detection** - Checks for valid favicon implementation
-   **External Link Validation** - Verifies all external links are accessible
-   **Deprecated Libraries** - Identifies outdated JavaScript libraries with security risks

### Data Security

-   **Data Leakage Detection** - Scans GitHub for potential credential leaks
-   **Domain Breach History** - Checks against Have I Been Pwned database
-   **Internationalization** - Verifies proper i18n implementation

## Manual Installation

If you prefer to run without Docker:

### Prerequisites

-   Python 3.8+
-   Required Python packages (see requirements.txt)

### Installation

```bash
git clone https://github.com/fabriziosalmi/websites-monitor.git
cd websites-monitor
pip install -r requirements.txt
```

### Configuration

1.  Copy the example configuration:

    ```bash
    cp config.yaml.example config.yaml
    ```

2.  Edit `config.yaml` with your settings:

    ```yaml
    api_keys:
      google_api_key: "your_google_api_key_here"
      github_token: "your_github_token_here"

    websites:
      - "example.com"
      - "anotherdomain.com"

    checks:
      mobile_friendly: true
      ssl_certificate: true
      # ... other checks
    ```

### Usage

Run the monitoring tool:

```bash
python main.py
```

## API Keys Setup

### Google Mobile-Friendly Test API

1.  Go to [Google Cloud Console](https://console.cloud.google.com/)
2.  Create a new project or select existing one
3.  Enable the "Search Console API"
4.  Create credentials (API Key)
5.  Add the API key to your configuration

### GitHub Token (for data leakage detection)

1.  Go to GitHub Settings > Developer settings > Personal access tokens
2.  Generate a new token with `public_repo` scope
3.  Add the token to your configuration

### Have I Been Pwned API (optional)

For enhanced breach detection, you can obtain an API key from [Have I Been Pwned](https://haveibeenpwned.com/API/Key)

## Output Format

The tool provides color-coded results for each check:

-   🟢 **Green**: Check passed, no issues found
-   🟡 **Yellow**: Warning, minor issues or suboptimal configuration
-   🟠 **Orange**: Moderate issues requiring attention
-   🔴 **Red**: Critical issues requiring immediate attention
-   ⚪ **White**: Check failed due to errors or unavailable

## Example Output

```
Website Security Analysis for example.com
========================================
✅ SSL Certificate: 🟢 (Valid until 2024-12-31)
✅ HSTS Headers: 🟢 (Strong configuration)
✅ Mixed Content: 🟢 (No mixed content found)
⚠️  Mobile Friendly: 🟡 (Minor responsive issues)
❌ DNSSEC: 🔴 (Not configured)
✅ External Links: 🟢 (All links valid)
```

## Support

For any issues or suggestions regarding this project, feel free to open an issue on GitHub.

---

This report was automatically generated on 2025-06-02 21:27:21 UTC.

| Website | Domain breach | Domain Expiration | SSL Certificate | DNS Blacklists | DomainsBlacklists | HSTS | XSS Protection | Redirect chains | Pagespeed | Load Time | Rate Limiting | CDN | Brotli | Deprecated Libraries | Client Rendering | Mixed Content | Content-Type | i18n | FLoC | AMP | Robots.txt | Sitemap | Favicon | Alt Tags | Open Graph | Semantic Markup | Ad Tracking | WHOIS Privacy | Privacy Exposure |
|---------|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
audiolibri.org | 🟢 | 🟢 (333 days left) | 🟠 (16 days left) | 🔴 | 🟢 | 🔴 | 🔴 | 🟢 | ⚪ | 🟢 | 🔴 | 🟢 | 🔴 | 🟢 | 🟠 | 🟢 | 🟢 | 🟡 | 🔴 | 🔴 | ⚪ | 🔴 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🔴 |
example.com | 🟢 | 🟡 (71 days left) | 🟢 (227 days left) | 🟢 | 🟢 | 🔴 | 🔴 | 🟢 | ⚪ | 🟢 | 🔴 | 🔴 | 🔴 | 🟢 | 🟢 | 🟢 | 🔴 | ⚪ | 🔴 | 🔴 | ⚪ | 🔴 | 🔴 | 🟢 | 🔴 | 🔴 | 🟢 | 🟢 | 🟢 |

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Security

If you discover any security vulnerabilities, please report them responsibly by emailing the maintainers rather than opening a public issue.

## Contributing

1.  Fork the repository
2.  Create a feature branch
3.  Make your changes
4.  Add tests if applicable
5.  Submit a pull request
