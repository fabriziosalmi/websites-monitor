# Website Monitor

[![GitHub Workflow Status](https://github.com/fabriziosalmi/websites-monitor/actions/workflows/create-report.yml/badge.svg)](https://github.com/fabriziosalmi/websites-monitor/actions/workflows/create-report.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://hub.docker.com/r/fabriziosalmi/websites-monitor)

A comprehensive website monitoring framework with both automated daily checks and a powerful web interface. Monitor the health, security, performance, and compliance of your websites with 53+ different checks organized into logical categories.

## 📑 Quick Links

- [🚀 Quick Start](#-quick-start) - Get up and running in minutes
- [✨ Features](#-features) - What Website Monitor can do
- [📖 How to Use](#-how-to-use) - Detailed usage instructions
- [🐳 Docker Deployment](docs/DOCKER.md) - Docker setup guide
- [🤝 Contributing](CONTRIBUTING.md) - How to contribute
- [📚 API Documentation](#-api-documentation) - API reference
- [🔧 Troubleshooting](#-troubleshooting) - Common issues and solutions
- [📝 Changelog](CHANGELOG.md) - Version history and changes

## Screenshot

![screenshot](https://github.com/fabriziosalmi/websites-monitor/blob/main/screenshot.png?raw=true)

## 🚀 Quick Start

### Web Interface
Run the local web interface for immediate testing:
```bash
python api.py
```
Then visit `http://localhost:8000` for the interactive web interface.

### Docker
Run with Docker for easy deployment:
```bash
docker run -p 8000:8000 fabriziosalmi/websites-monitor
```

### GitHub Actions
Use the automated daily monitoring by configuring `config.yaml` and enabling GitHub Actions.

## ✨ Features

### 🌐 **Web Interface**
- Interactive HTML interface for real-time website analysis
- Category-based check selection for easier management
- Mobile-responsive design
- Real-time results display
- No setup required - just run and test

### 🔄 **Automated Monitoring**
- Daily automated checks via GitHub Actions
- Configurable scheduling and reporting
- Automatic markdown report generation
- GitHub integration with commit updates

### 📊 **Comprehensive Analysis - 53+ Checks**
Organized into 7 logical categories:

#### 🛡️ **Security & Protection (10 checks)**
- SSL Certificate validation
- SSL Cipher Strength analysis
- Security Headers assessment
- HSTS (HTTP Strict Transport Security)
- XSS Protection verification
- CORS Headers analysis
- Mixed Content detection
- Subresource Integrity check
- Rate Limiting detection
- Data Leakage prevention

#### ⚡ **Performance & Speed (8 checks)**
- PageSpeed Insights score
- Website Load Time measurement
- Server Response Time analysis
- Brotli Compression detection
- Asset Minification verification
- CDN Detection
- Redirect Chains analysis
- Redirects optimization

#### 🎯 **SEO & Content (9 checks)**
- Sitemap validation
- Robots.txt verification
- Open Graph Protocol compliance
- Alt Tags for images
- Semantic Markup analysis
- URL Canonicalization
- Favicon presence
- Broken Links detection
- External Links analysis

#### 🌍 **Domain & DNS (7 checks)**
- Domain Expiration monitoring
- DNSSEC validation
- DNS Blacklist checking
- Domain Breach detection
- Domain Blacklists verification
- Subdomain Enumeration
- Email Domain validation

#### 🔒 **Privacy & Tracking (10 checks)**
- Cookie Policy compliance
- Cookie Flags verification
- Cookie Duration analysis
- Cookie SameSite attributes
- Ad & Tracking detection
- FLoC (Federated Learning of Cohorts) detection
- Privacy Exposure assessment
- WHOIS Protection verification
- Third-Party Requests monitoring
- Third-Party Resources analysis

#### 📱 **Accessibility & Mobile (5 checks)**
- Accessibility compliance
- Mobile Friendly testing
- AMP Compatibility
- Internationalization support
- Browser Compatibility

#### 🔧 **Technical & Infrastructure (4 checks)**
- Content-Type Headers validation
- CMS Detection
- Client-Side Rendering analysis
- Deprecated Libraries detection

### 🛠️ **Multiple Interfaces**
- **Web UI**: Interactive browser-based interface
- **API**: RESTful endpoints for integration
- **CLI**: Command-line interface for automation
- **GitHub Actions**: Automated daily monitoring

### 📚 **Documentation & API**
- Swagger UI at `/api/docs` for interactive API testing
- ReDoc documentation at `/api/redoc` for detailed API reference
- Comprehensive API endpoints for all monitoring functions
- Docker support for easy deployment

## 📖 How to Use

### 📋 Prerequisites

Before using Website Monitor, ensure you have:

- **Python**: Version 3.11 or higher
- **pip**: Python package manager
- **Git**: For cloning the repository
- **Chrome/Chromium**: Required for some checks (automatically managed in Docker)
- **Optional**: Docker and Docker Compose for containerized deployment

### 💻 Local Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/fabriziosalmi/websites-monitor.git
   cd websites-monitor
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install fastapi uvicorn[standard] pydantic
   ```

3. **Configure (Optional)**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings (e.g., PAGESPEED_API_KEY)
   ```

4. **Run the Web Interface**:
   ```bash
   python api.py
   ```
   Then open `http://localhost:8000` in your browser.

### 🌐 Web Interface Usage

1. **Quick Start**:
   ```bash
   python api.py
   ```
   Open `http://localhost:8000` in your browser.

2. **Using the Interface**:
   - Enter a website URL in the input field
   - Select check categories you want to run
   - Click "Run Checks" to analyze the website
   - View real-time results with detailed explanations

3. **Categories Available**:
   - Toggle entire categories on/off for easier management
   - Each category contains multiple related checks
   - Mobile-responsive interface works on all devices

### 🐳 Docker Usage

1. **Run with Docker**:
   ```bash
   docker run -p 8000:8000 fabriziosalmi/websites-monitor
   ```

2. **Build from Source**:
   ```bash
   docker build -t websites-monitor .
   docker run -p 8000:8000 websites-monitor
   ```

### 🔄 GitHub Actions Setup

Automate website monitoring with GitHub Actions that runs checks daily and commits results to your repository.

#### Step-by-Step Guide:

1. **Fork This Repository**: 
   - Click the "Fork" button at the top of this page
   - This creates your own copy of the repository

2. **Configure Websites to Monitor**:
   - Edit `config.yaml` in your fork
   - Add your websites under the `websites:` section:
   ```yaml
   websites:
     - yourwebsite.com
     - example.com
   ```
   - **Note**: Don't include `http://` or `https://` - just the domain

3. **Enable GitHub Actions**:
   - Go to the "Actions" tab in your repository
   - Click "I understand my workflows, go ahead and enable them"
   - Ensure Actions have write permissions:
     - Settings → Actions → General → Workflow permissions
     - Select "Read and write permissions"

4. **Set PageSpeed API Key** (Optional but Recommended):
   - Get a free API key from [Google PageSpeed Insights](https://developers.google.com/speed/docs/insights/v5/get-started)
   - In your repository: Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `PAGESPEED_API_KEY`
   - Value: Your API key
   - Click "Add secret"

5. **Customize Report Template** (Optional):
   - Edit `report_template.md` to customize the report format
   - The default template is minimal; you can add your own headers and sections

6. **Trigger First Run**:
   - Make any commit to trigger the workflow
   - Or go to Actions → Create report → Run workflow
   - Results will be committed to `README.md` (or your configured `output_file`)

#### Scheduling

By default, the workflow runs daily at 4 AM UTC. To change the schedule:

Edit `.github/workflows/create-report.yml`:
```yaml
on:
  schedule:
    - cron: '0 4 * * *'  # Change this cron expression
```

Common cron examples:
- `'0 */6 * * *'` - Every 6 hours
- `'0 0 * * 1'` - Every Monday at midnight
- `'0 12 * * *'` - Daily at noon

### 🛠️ API Usage

The Website Monitor provides a comprehensive REST API for programmatic access to all monitoring functions.

#### Available Endpoints:

- `GET /` - Web interface
- `POST /monitor` - Run checks on a website
- `GET /api/docs` - Swagger UI documentation
- `GET /api/redoc` - ReDoc API documentation
- `GET /health` - Health check endpoint
- `GET /checks` - List all available checks

#### Basic Example - Single Website Check:

```bash
curl -X POST "http://localhost:8000/monitor" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "example.com",
       "checks": ["ssl_cert", "security_headers", "pagespeed_performances"]
     }'
```

#### Response Format:

```json
{
  "url": "example.com",
  "timestamp": "2024-11-15T19:30:00Z",
  "results": {
    "ssl_cert": "🟢 Valid until 2025-12-31",
    "security_headers": "🟢 All security headers present",
    "pagespeed_performances": "🟢 Score: 95/100"
  },
  "summary": {
    "total": 3,
    "passed": 3,
    "failed": 0,
    "errors": 0
  }
}
```

#### Advanced Example - Multiple Websites:

```bash
curl -X POST "http://localhost:8000/monitor" \
     -H "Content-Type: application/json" \
     -d '{
       "websites": ["example.com", "google.com"],
       "checks": ["ssl_cert", "hsts", "xss_protection"],
       "timeout": 60
     }'
```

#### Check All Security Features:

```bash
curl -X POST "http://localhost:8000/monitor" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "example.com",
       "categories": ["security"]
     }'
```

#### List Available Checks:

```bash
curl http://localhost:8000/checks
```

#### Health Check:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.3.0",
  "checks_available": 53
}
```

## ⚙️ Configuration Options

The `config.yaml` file supports:

- `websites`: List of URLs to monitor (required)
- `output_file`: Report filename (default: `report.md`)
- `max_workers`: Concurrent tasks for checks (default: 4)
- `timeout`: Default timeout in seconds (default: 30)
- `report_template`: Template filename (default: `report_template.md`)
- `github_workflow_badge`: Workflow badge URL
- `pagespeed_api_key`: Google PageSpeed API key (can also be set via environment variable)

## 🔧 Customizing Checks

You can customize which checks run and add new checks to extend the monitoring capabilities.

### Adding New Checks

1. **Create a Check File**: Create a new file in the `checks/` directory following the naming pattern `check_<feature>.py`

2. **Implement the Check Function**: Follow this template:
   ```python
   def check_<feature>(url: str, timeout: int = 30) -> str:
       """
       Description of what this check does.
       
       Args:
           url: Website URL to check
           timeout: Request timeout in seconds
       
       Returns:
           Status emoji with description
       """
       try:
           # Your check logic here
           return "🟢 Check passed"
       except Exception as e:
           return f"⚪ Error: {str(e)}"
   ```

3. **Register the Check**: Add imports to `main.py` and `api.py`

4. **Update Documentation**: Add the check to README.md in the appropriate category

For detailed instructions, see [CONTRIBUTING.md](CONTRIBUTING.md#adding-new-checks).

### Available Check Categories

All 53 checks are organized into these categories:

#### 🛡️ Security & Protection (10 checks)
| Check | Description |
|-------|-------------|
| `ssl_cert` | Validates SSL/TLS certificate validity and expiration |
| `ssl_cipher_strength` | Analyzes SSL/TLS cipher strength and configuration |
| `security_headers` | Checks for essential security headers |
| `hsts` | Verifies HTTP Strict Transport Security |
| `xss_protection` | Checks XSS protection headers |
| `cors_headers` | Analyzes CORS configuration |
| `mixed_content` | Detects mixed HTTP/HTTPS content |
| `subresource_integrity` | Checks SRI implementation |
| `rate_limiting` | Tests for rate limiting |
| `data_leakage` | Scans for potential data leaks |

#### ⚡ Performance & Speed (8 checks)
| Check | Description |
|-------|-------------|
| `pagespeed_performances` | Google PageSpeed Insights score |
| `website_load_time` | Measures total page load time |
| `server_response_time` | Measures server response latency |
| `brotli_compression` | Checks for Brotli compression |
| `asset_minification` | Verifies CSS/JS minification |
| `cdn` | Detects CDN usage |
| `redirect_chains` | Analyzes redirect chains |
| `redirects` | Checks redirect optimization |

#### 🎯 SEO & Content (9 checks)
| Check | Description |
|-------|-------------|
| `sitemap` | Validates sitemap.xml existence |
| `robot_txt` | Checks robots.txt configuration |
| `open_graph_protocol` | Validates Open Graph meta tags |
| `alt_tags` | Checks image alt attributes |
| `semantic_markup` | Analyzes HTML5 semantic elements |
| `url_canonicalization` | Checks canonical URLs |
| `favicon` | Verifies favicon presence |
| `broken_links` | Detects broken internal links |
| `external_links` | Analyzes external link quality |

#### 🌍 Domain & DNS (7 checks)
| Check | Description |
|-------|-------------|
| `domain_expiration` | Monitors domain expiration date |
| `dnssec` | Validates DNSSEC configuration |
| `dns_blacklist` | Checks DNS blacklists |
| `domain_breach` | Checks breach databases |
| `domainsblacklists_blacklist` | Additional blacklist verification |
| `subdomain_enumeration` | Discovers subdomains |
| `email_domain` | Validates email domain configuration |

#### 🔒 Privacy & Tracking (10 checks)
| Check | Description |
|-------|-------------|
| `cookie_policy` | Checks cookie policy compliance |
| `cookie_flags` | Validates secure cookie flags |
| `cookie_duration` | Analyzes cookie expiration |
| `cookie_samesite_attribute` | Checks SameSite attributes |
| `ad_and_tracking` | Detects advertising trackers |
| `floc` | Checks FLoC opt-out |
| `privacy_exposure` | Scans for privacy issues |
| `privacy_protected_whois` | Verifies WHOIS privacy |
| `third_party_requests` | Monitors third-party requests |
| `third_party_resources` | Analyzes third-party resources |

#### 📱 Accessibility & Mobile (5 checks)
| Check | Description |
|-------|-------------|
| `accessibility` | WCAG accessibility compliance |
| `mobile_friendly` | Mobile-friendliness testing |
| `amp_compatibility` | AMP page validation |
| `internationalization` | i18n support verification |
| `browser_compatibility` | Cross-browser compatibility |

#### 🔧 Technical & Infrastructure (4 checks)
| Check | Description |
|-------|-------------|
| `content_type_headers` | Validates Content-Type headers |
| `cms_used` | Detects CMS platform |
| `clientside_rendering` | Checks for CSR implementation |
| `deprecated_libraries` | Scans for outdated libraries |

### Check Format Reference

Each check returns a status string in the format:
```
<emoji> <detailed_message>
```

Examples:
- `🟢 Valid until 2025-12-31` (SSL certificate)
- `🔴 Missing: X-Frame-Options, X-Content-Type-Options` (Security headers)
- `🟡 Score: 72/100 - Could be improved` (PageSpeed)
- `⚪ Error: Connection timeout` (Any check failure)

## 📊 Understanding Results

### Status Indicators:

All checks return one of four status indicators:

| Emoji | Status | Meaning |
|-------|--------|---------|
| 🟢 | **Success** | Check passed - no issues detected |
| 🔴 | **Failed** | Check failed - issue found that needs attention |
| 🟡 | **Warning** | Check completed with warnings - review recommended |
| ⚪ | **Error** | Check could not be completed due to technical error |

### Result Formats

#### Web Interface:
- **Real-time Display**: Results appear as checks complete
- **Color Coding**: Visual indicators match the emoji status
- **Detailed Explanations**: Each result includes specific details
- **Category Organization**: Results grouped by check category
- **Mobile Responsive**: Works on all devices

#### API Response:
```json
{
  "url": "example.com",
  "results": {
    "ssl_cert": "🟢 Valid until 2025-12-31",
    "security_headers": "🔴 Missing: X-Frame-Options, X-Content-Type-Options",
    "hsts": "🟢 Max-age: 31536000",
    "pagespeed": "🟡 Score: 72/100 - Could be improved"
  }
}
```

#### GitHub Reports:
- **Markdown Tables**: Easy-to-read tabular format
- **Automatic Updates**: Updated daily via GitHub Actions
- **Historical Tracking**: Track changes over time through git commits
- **Badge Integration**: Status badges for quick overview

### Interpreting Specific Results

**Security Checks** (🛡️):
- 🟢 means your security measures are properly configured
- 🔴 indicates missing or misconfigured security features
- Fix these immediately to protect your users

**Performance Checks** (⚡):
- 🟢 indicates good performance
- 🟡 suggests optimization opportunities
- 🔴 means significant performance issues that affect user experience

**SEO Checks** (🎯):
- 🟢 means search engines can properly index your site
- 🔴 indicates missing elements that harm search rankings

**Accessibility Checks** (📱):
- 🟢 means your site is accessible to all users
- 🔴 indicates barriers that prevent some users from accessing your content

## 🛡️ Security Features

- **SSL/TLS Analysis**: Certificate validation, cipher strength, HSTS
- **Header Security**: Security headers, XSS protection, CORS
- **Content Security**: Mixed content detection, subresource integrity
- **Privacy Protection**: Cookie analysis, tracking detection, data leakage

## ⚡ Performance Monitoring

- **Speed Analysis**: Load times, server response, PageSpeed scores
- **Optimization**: Compression, minification, CDN detection
- **Network**: Redirect chains, external resource analysis

## 🔍 SEO & Accessibility

- **SEO Compliance**: Sitemaps, robots.txt, meta tags, structured data
- **Accessibility**: WCAG compliance, mobile-friendly testing
- **Content Quality**: Alt tags, semantic markup, internationalization

## 🐳 Docker Deployment

The project includes full Docker support for easy deployment:

```bash
# Available on Docker Hub
docker pull fabriziosalmi/websites-monitor

# Run with custom port
docker run -p 3000:8000 fabriziosalmi/websites-monitor

# Run with environment variables
docker run -e PAGESPEED_API_KEY=your_key fabriziosalmi/websites-monitor
```

For detailed Docker setup instructions, see [docs/DOCKER.md](docs/DOCKER.md).

## 🔧 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000

# Or use a different port
python api.py --port 8001
```

#### Chrome/ChromeDriver Issues
```bash
# Install Chrome dependencies on Linux
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver

# Or use Docker which handles this automatically
docker-compose up
```

#### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
pip install fastapi uvicorn[standard] pydantic
```

#### PageSpeed API Errors
- Ensure your `PAGESPEED_API_KEY` is set correctly in `.env` or as an environment variable
- Verify the API key is valid at https://developers.google.com/speed/docs/insights/v5/get-started
- Check your API quota hasn't been exceeded

#### Timeout Errors
```yaml
# Increase timeout in config.yaml
timeout: 60  # Increase from default 30 seconds
```

For more help, check:
- [GitHub Issues](https://github.com/fabriziosalmi/websites-monitor/issues)
- [Documentation](docs/DOCKER.md)
- API docs at http://localhost:8000/api/docs

## ❓ Frequently Asked Questions (FAQ)

### General Questions

**Q: How many websites can I monitor?**  
A: There's no hard limit, but for performance reasons, we recommend monitoring 10-50 websites. For larger deployments, consider adjusting `max_workers` in config.yaml or running multiple instances.

**Q: How long does each check take?**  
A: Individual checks typically take 1-5 seconds. A full scan of all 53 checks usually completes in 30-60 seconds per website, depending on network conditions and website response times.

**Q: Do I need all the dependencies for just the API?**  
A: For the web API, you need `requests`, `beautifulsoup4`, `dnspython`, `python-whois`, `fastapi`, `uvicorn`, and `pydantic`. Selenium and Chrome are only needed for certain advanced checks.

### Configuration Questions

**Q: Can I run only specific checks?**  
A: Yes! When using the API, specify the checks you want:
```bash
curl -X POST "http://localhost:8000/monitor" \
  -H "Content-Type: application/json" \
  -d '{"url": "example.com", "checks": ["ssl_cert", "security_headers"]}'
```

**Q: How do I disable a specific check?**  
A: Remove it from the checks list when calling the API, or modify the `WebsiteMonitor` class in `main.py` to exclude it from default checks.

**Q: Can I customize the timeout for slow websites?**  
A: Yes, edit `config.yaml`:
```yaml
timeout: 60  # Increase from default 30 seconds
```

### API Questions

**Q: Can I use the API without the web interface?**  
A: Yes! Just call the API endpoints directly. The web interface is optional.

**Q: Is there rate limiting on the API?**  
A: There's no built-in rate limiting. For production use, consider adding nginx or another reverse proxy with rate limiting.

**Q: Can I get results in JSON format?**  
A: Yes, all API endpoints return JSON by default. The web interface is just a user-friendly view of the JSON data.

### GitHub Actions Questions

**Q: Why isn't my workflow running?**  
A: Check that:
- GitHub Actions is enabled in your repository
- The workflow file is in `.github/workflows/`
- Actions have write permissions (Settings → Actions → General)

**Q: The workflow fails with "No changes to commit"**  
A: This is normal if the results haven't changed since the last run. It's not an error.

**Q: Can I trigger the workflow manually?**  
A: Yes! Go to Actions → Create report → Run workflow.

### Docker Questions

**Q: Do I need Docker to use Website Monitor?**  
A: No, Docker is optional. You can run it directly with Python, but Docker simplifies deployment.

**Q: Can I use docker-compose for production?**  
A: Yes! Use `docker-compose --profile production up -d` for the full production stack with nginx, Redis, and PostgreSQL.

**Q: How do I update the Docker image?**  
A: Pull the latest image:
```bash
docker pull fabriziosalmi/websites-monitor
docker-compose up -d
```

## 📚 API Documentation

### Interactive Documentation:
- **Swagger UI**: Visit `/api/docs` for interactive API testing
- **ReDoc**: Visit `/api/redoc` for detailed API reference

### Integration Examples:
- REST API endpoints for all monitoring functions
- JSON response format for easy integration
- Comprehensive error handling and status codes

## 📁 Project Structure

```
websites-monitor/
├── api.py                 # FastAPI web server and REST API
├── main.py               # Core monitoring logic and check orchestration
├── scheduler.py          # Scheduled monitoring service
├── config.yaml           # Configuration file for websites and settings
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Docker Compose configuration
├── checks/               # Individual check implementations
│   ├── check_ssl_cert.py
│   ├── check_security_headers.py
│   └── ... (53 check files)
├── docs/                 # Additional documentation
│   └── DOCKER.md        # Docker deployment guide
├── .env.example         # Environment variables template
├── CONTRIBUTING.md      # Contribution guidelines
└── README.md            # This file
```

### Key Components

- **`api.py`**: Web interface and RESTful API endpoints
- **`main.py`**: Core monitoring engine that orchestrates all checks
- **`scheduler.py`**: Background service for periodic monitoring
- **`checks/`**: Modular check implementations - each file contains one check
- **`config.yaml`**: Website list and monitoring configuration
- **`.env`**: Environment variables (API keys, secrets)

## 🤝 Contributing

We welcome contributions! To get started:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure everything works
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

For detailed guidelines, please see [CONTRIBUTING.md](CONTRIBUTING.md).

### Adding New Checks

To add a new monitoring check:

1. Create a new check file in the `checks/` directory
2. Follow the existing check format (return 🟢, 🔴, 🟡, or ⚪)
3. Register the check in `main.py` and `api.py`
4. Update documentation
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed instructions.

## 🎯 Best Practices

### For Monitoring Multiple Websites

**Optimize Performance:**
```yaml
# config.yaml
max_workers: 4  # Adjust based on your system resources
timeout: 45     # Increase for slow websites
```

**Selective Checking:**  
Instead of running all 53 checks, focus on the most important ones for your use case:
```bash
# Security-focused monitoring
curl -X POST "http://localhost:8000/monitor" \
  -d '{"url": "example.com", "categories": ["security"]}'

# Performance-focused monitoring  
curl -X POST "http://localhost:8000/monitor" \
  -d '{"url": "example.com", "categories": ["performance"]}'
```

### For GitHub Actions

**Optimize Workflow:**
- Run critical checks daily, comprehensive checks weekly
- Use caching for dependencies
- Set appropriate timeout values
- Monitor Actions usage limits

**Example schedule:**
```yaml
# Daily critical checks
- cron: '0 4 * * *'

# Weekly comprehensive scan
- cron: '0 4 * * 0'
```

### For Production Deployment

**Security:**
- Use environment variables for sensitive data
- Enable SSL/TLS for API endpoints
- Implement rate limiting
- Use Docker secrets for production credentials

**Performance:**
- Deploy behind a reverse proxy (nginx)
- Enable caching with Redis
- Use PostgreSQL for persistent storage
- Scale API service horizontally with multiple containers

**Monitoring:**
- Set up health check monitoring
- Configure log aggregation
- Track API response times
- Monitor system resources

See [docs/DOCKER.md](docs/DOCKER.md) for production deployment details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Website Monitor uses several excellent open-source projects:

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework for building APIs
- [Selenium](https://www.selenium.dev/) - Browser automation
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing
- [python-whois](https://pypi.org/project/python-whois/) - WHOIS lookups
- [dnspython](https://www.dnspython.org/) - DNS toolkit
- [Docker](https://www.docker.com/) - Containerization platform

Special thanks to all [contributors](https://github.com/fabriziosalmi/websites-monitor/graphs/contributors) who help improve this project!

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/fabriziosalmi/websites-monitor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/fabriziosalmi/websites-monitor/discussions)
- **Documentation**: This README and [docs/](docs/)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

---

<div align="center">

**[⬆ Back to Top](#website-monitor)**

Made with ❤️ by [Fabrizio Salmi](https://github.com/fabriziosalmi)

[![GitHub stars](https://img.shields.io/github/stars/fabriziosalmi/websites-monitor?style=social)](https://github.com/fabriziosalmi/websites-monitor/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/fabriziosalmi/websites-monitor?style=social)](https://github.com/fabriziosalmi/websites-monitor/network/members)

</div>

