# Website Monitor

A comprehensive website monitoring system that performs 53+ automated checks across security, performance, SEO, accessibility, and privacy categories. Built with Python, FastAPI, and Docker for easy deployment and scalability.

## Features Overview

This monitoring system provides extensive website analysis with 53+ individual checks organized into the following categories:

### 🔒 Security Checks (15+)
- SSL/TLS certificate validation and expiration monitoring
- HTTP security headers analysis (HSTS, CSP, X-Frame-Options, etc.)
- Mixed content detection (HTTP resources on HTTPS pages)
- Cookie security attributes validation
- Subdomain takeover vulnerability detection
- DNS security configuration checks
- HTTPS redirect validation
- Security policy compliance verification

### ⚡ Performance Monitoring (12+)
- Page load time measurement and analysis
- Resource loading performance metrics
- Image optimization and compression analysis
- JavaScript and CSS minification checks
- CDN usage detection and optimization
- Cache header validation
- Resource size optimization recommendations
- Core Web Vitals monitoring

### 🎯 SEO Analysis (10+)
- Meta tags validation (title, description, keywords)
- Open Graph and Twitter Card metadata
- Structured data (Schema.org) validation
- Canonical URL verification
- Robots.txt analysis
- XML sitemap detection and validation
- Internal linking structure analysis
- SEO best practices compliance

### ♿ Accessibility Checks (8+)
- WCAG compliance validation
- Alt text verification for images
- Color contrast ratio analysis
- Keyboard navigation support
- ARIA attributes validation
- Form accessibility checks
- Semantic HTML structure verification

### 🛡️ Privacy & Compliance (8+)
- Cookie policy and GDPR compliance
- Privacy policy detection
- Third-party tracker analysis
- Data collection transparency checks
- User consent mechanism validation
- Regional compliance verification (CCPA, GDPR)

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.9+ (for local development)

### Docker Deployment (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/fabriziosalmi/websites-monitor
cd websites-monitor
```

2. Start the monitoring system:
```bash
docker-compose up -d
```

3. Access the services:
- **API Documentation**: http://localhost:8000/docs
- **Monitoring API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure monitoring targets in `config.yaml`

3. Run the API server:
```bash
python api.py
```

4. Run the scheduler (in separate terminal):
```bash
python scheduler.py
```

## Configuration

### config.yaml
Configure your monitoring targets and settings in the `config.yaml` file:

```yaml
monitoring:
  websites:
    - url: "https://example.com"
      name: "Example Website"
      checks: ["all"]  # or specific check names
    - url: "https://mysite.com"
      name: "My Site"
      checks: ["security", "performance"]
  
  schedule:
    interval: 3600  # seconds between checks
    
  notifications:
    email:
      enabled: true
      smtp_server: "smtp.gmail.com"
      port: 587
      username: "your-email@gmail.com"
      password: "your-password"
      recipients: ["admin@example.com"]
```

## API Endpoints

### Core Endpoints

#### GET /health
Health check endpoint for monitoring service status.

#### POST /monitor
Trigger immediate monitoring of configured websites.

#### GET /results
Retrieve latest monitoring results.

#### GET /results/{website_id}
Get results for a specific website.

#### GET /checks
List all available monitoring checks.

## Detailed Check Categories

### Security Checks

| Check Name | Description | Critical |
|------------|-------------|----------|
| `ssl_certificate` | Validates SSL certificate and expiration | ✅ |
| `https_redirect` | Ensures HTTP redirects to HTTPS | ✅ |
| `security_headers` | Analyzes security headers (HSTS, CSP, etc.) | ✅ |
| `mixed_content` | Detects insecure HTTP resources on HTTPS | ✅ |
| `cookie_security` | Validates secure cookie attributes | ⚠️ |
| `subdomain_takeover` | Checks for subdomain takeover risks | ✅ |
| `dns_security` | Validates DNS configuration | ⚠️ |
| `xss_protection` | Checks XSS protection headers | ⚠️ |
| `clickjacking_protection` | Validates X-Frame-Options header | ⚠️ |
| `content_security_policy` | Analyzes CSP implementation | ⚠️ |

### Performance Checks

| Check Name | Description | Threshold |
|------------|-------------|-----------|
| `page_load_time` | Measures total page load time | < 3s |
| `time_to_first_byte` | TTFB measurement | < 200ms |
| `image_optimization` | Checks image compression | Auto |
| `css_minification` | Validates CSS minification | Auto |
| `js_minification` | Validates JavaScript minification | Auto |
| `gzip_compression` | Checks compression headers | Auto |
| `cdn_usage` | Detects CDN implementation | Info |
| `cache_headers` | Validates caching configuration | Auto |
| `resource_count` | Counts HTTP requests | < 50 |

### SEO Checks

| Check Name | Description | Impact |
|------------|-------------|--------|
| `meta_title` | Validates page title | High |
| `meta_description` | Checks meta description | High |
| `meta_keywords` | Analyzes keyword tags | Low |
| `open_graph` | Validates OG metadata | Medium |
| `twitter_cards` | Checks Twitter Card data | Medium |
| `structured_data` | Schema.org validation | High |
| `canonical_url` | Canonical URL verification | High |
| `robots_txt` | Robots.txt analysis | Medium |
| `sitemap_xml` | XML sitemap detection | Medium |

## Monitoring Results

Results are stored locally in JSON format and include:

- **Timestamp**: When the check was performed
- **Status**: Pass/Fail/Warning for each check
- **Details**: Specific findings and recommendations
- **Performance Metrics**: Timing and size measurements
- **Scores**: Overall health scores by category

### Result Structure
```json
{
  "website": "https://example.com",
  "timestamp": "2023-12-01T12:00:00Z",
  "overall_score": 85,
  "categories": {
    "security": {
      "score": 90,
      "checks": {
        "ssl_certificate": {
          "status": "pass",
          "details": "Valid certificate, expires 2024-06-01"
        }
      }
    }
  }
}
```

## Deployment Options

### Docker Compose (Production)
The included `docker-compose.yml` provides a complete production setup with:
- API service container
- Scheduler service container
- Health checks and restart policies
- Volume mounting for persistent data

### Kubernetes
For Kubernetes deployment, convert the Docker Compose configuration or use the provided Helm charts (if available).

### Cloud Deployment
The system can be deployed on:
- AWS (ECS, EKS, or EC2)
- Google Cloud Platform (GKE or Compute Engine)
- Azure (AKS or Container Instances)
- DigitalOcean (App Platform or Droplets)

## Monitoring Schedule

The scheduler runs automatically and performs:
- **Regular Checks**: Every hour (configurable)
- **Deep Scans**: Daily comprehensive analysis
- **Quick Health Checks**: Every 15 minutes
- **Alert Monitoring**: Continuous for critical issues

## Alerting & Notifications

Configure notifications for:
- **Critical Security Issues**: Immediate alerts
- **Performance Degradation**: Threshold-based notifications
- **Certificate Expiration**: 30/7/1 day warnings
- **Downtime Detection**: Instant notifications
- **Regular Reports**: Daily/weekly summaries

### Supported Notification Channels
- Email (SMTP)
- Slack webhooks
- Discord webhooks
- Microsoft Teams
- PagerDuty integration
- Custom webhook endpoints

## Troubleshooting

### Common Issues

**Container Restart Loops**
```bash
# Check container logs
docker logs websites-monitor-scheduler-1
docker logs websites-monitor-api-1

# Rebuild with no cache
docker-compose build --no-cache
docker-compose up -d
```

**Missing Dependencies**
Ensure all required packages are installed:
```bash
pip install fastapi uvicorn pydantic requests beautifulsoup4 lxml
```

**Configuration Errors**
Validate your `config.yaml` syntax and required fields.

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export DEBUG=true
```

## Development

### Adding New Checks
1. Create a new check module in the `checks/` directory
2. Implement the check function following the standard interface
3. Add the check to the main monitoring configuration
4. Update documentation and tests

### Check Interface
```python
def check_example(url: str, config: dict) -> dict:
    """
    Perform example check on the given URL.
    
    Args:
        url: Target URL to check
        config: Check configuration parameters
        
    Returns:
        dict: Check result with status, details, and metrics
    """
    return {
        "status": "pass|fail|warning",
        "details": "Human readable description",
        "metrics": {"key": "value"},
        "recommendations": ["suggestion1", "suggestion2"]
    }
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all checks pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For any issues or suggestions regarding this project, feel free to open an issue on GitHub.

---





This report was automatically generated on 2025-02-04 04:06:54 UTC.

| Website | Domain breach | Domain Expiration | SSL Certificate | DNS Blacklists | DomainsBlacklists | HSTS | XSS Protection | Redirect chains | Pagespeed | Load Time | Rate Limiting | CDN | Brotli | Deprecated Libraries | Client Rendering | Mixed Content | Content-Type | i18n | FLoC | AMP | Robots.txt | Sitemap | Favicon | Alt Tags | Open Graph | Semantic Markup | Ad Tracking | WHOIS Privacy | Privacy Exposure |
|---------|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
audiolibri.org | ⚪ | 🟢 (87 days left) | 🟢 (32 days left) | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 99 | 🟢 | 🔴 | 🟢 | 🟢 | 🟡 | 🔴 | 🔴 | 🟢 | 🟢 | 🔴 | 🔴 | ⚪ | 🔴 | 🟢 | 🔴 | 🔴 | 🔴 | 🟢 | 🟢 | 🔴 |
example.com | ⚪ | 🟢 (189 days left) | 🔴 | 🟢 | 🟢 | 🔴 | 🔴 | ⚪ | 100 | 🟢 | ⚪ | ⚪ | ⚪ | 🟢 | 🟢 | 🟢 | 🔴 | ⚪ | 🔴 | 🔴 | ⚪ | 🔴 | 🔴 | 🟢 | 🔴 | 🔴 | 🟢 | 🔴 | ⚪ |
