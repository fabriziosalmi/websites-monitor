# Website Monitor

[![GitHub Workflow Status](https://github.com/fabriziosalmi/websites-monitor/actions/workflows/create-report.yml/badge.svg)](https://github.com/fabriziosalmi/websites-monitor/actions/workflows/create-report.yml)

A comprehensive website monitoring framework with both automated daily checks and a powerful web interface. Monitor the health, security, performance, and compliance of your websites with 53+ different checks organized into logical categories.

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
- Swagger UI at `/docs` for interactive API testing
- ReDoc documentation at `/redoc` for detailed API reference
- Comprehensive API endpoints for all monitoring functions
- Docker support for easy deployment

## 📖 How to Use

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

1. **Fork This Repository**: Start by forking this repository to your GitHub account.

2. **Configure Websites**:
   - Edit the `config.yaml` file
   - Add the websites you want to monitor:
   ```yaml
   websites:
     - audiolibri.org
     - example.com
   ```

3. **Enable GitHub Actions**:
   - Navigate to the "Actions" tab in your repository
   - Enable GitHub Actions with write permissions

4. **Set API Key Secret** (Optional):
   - Get a Google PageSpeed Insights API key
   - Add it as a repository secret named `PAGESPEED_API_KEY`

5. **Create Report Template**:
   - Create `report_template.md` in the root directory
   - Add your desired report template content

6. **Commit Changes**:
   - Commit and push to trigger the initial report generation

### 🛠️ API Usage

#### Available Endpoints:

- `GET /` - Web interface
- `POST /check` - Run checks on a website
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc API documentation
- `GET /health` - Health check endpoint

#### Example API Call:
```bash
curl -X POST "http://localhost:8000/check" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "example.com",
       "checks": ["ssl_certificate", "security_headers", "performance"]
     }'
```

## ⚙️ Configuration Options

The `config.yaml` file supports:

- `websites`: List of URLs to monitor
- `output_file`: Report filename (default: `README.md`)
- `max_workers`: Concurrent tasks for checks
- `timeout`: Default timeout in seconds
- `report_template`: Template filename (default: `report_template.md`)
- `github_workflow_badge`: Workflow badge URL
- `pagespeed_api_key`: Google PageSpeed API key

## 🔧 Customizing Checks

1. **Add New Checks**: Create new check functions in the `checks` directory
2. **Modify Existing**: Edit files in `checks/` directory
3. **Update Categories**: Modify the category organization in `main.py`
4. **Check Format**: Ensure functions return status emojis (🟢, 🔴, 🟡, ⚪)

## 📊 Understanding Results

### Status Indicators:
- 🟢 **Success**: Check passed successfully
- 🔴 **Failed**: Check failed or issue detected
- 🟡 **Warning**: Check completed with warnings
- ⚪ **Error**: Check could not be completed

### Web Interface:
- Real-time results display
- Detailed explanations for each check
- Category-based organization
- Mobile-friendly responsive design

### GitHub Reports:
- Automatic markdown table generation
- Daily updates via GitHub Actions
- Historical tracking through git commits
- Badge integration for status overview

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

```dockerfile
# Available on Docker Hub
docker pull fabriziosalmi/websites-monitor

# Run with custom port
docker run -p 3000:8000 fabriziosalmi/websites-monitor

# Run with environment variables
docker run -e PAGESPEED_API_KEY=your_key fabriziosalmi/websites-monitor
```

## 📚 API Documentation

### Interactive Documentation:
- **Swagger UI**: Visit `/docs` for interactive API testing
- **ReDoc**: Visit `/redoc` for detailed API reference

### Integration Examples:
- REST API endpoints for all monitoring functions
- JSON response format for easy integration
- Comprehensive error handling and status codes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add new checks in the `checks/` directory
4. Update documentation
5. Submit a pull request

## 📄 License

This project is open source. See the license file for details.

## 💬 Support

For issues or suggestions:
- Open a GitHub issue
- Check the documentation at `/docs`
- Review existing issues and discussions

---

*This comprehensive monitoring framework provides everything you need to keep your websites secure, fast, and compliant. Whether you prefer the interactive web interface, automated GitHub Actions, or API integration - Website Monitor has you covered.*

---

## 📊 Latest Monitoring Report

This report was automatically generated on 2025-06-02 23:24:19 UTC.

| Website | SSL Certificate | SSL Cipher Strength | Security Headers | HSTS | XSS Protection | CORS Headers | Mixed Content | Subresource Integrity | Rate Limiting | Data Leakage | Pagespeed | Website Load Time | Server Response Time | Brotli Compression | Asset Minification | CDN | Redirect Chains | Redirects | Sitemap | Robots.txt | Open Graph Protocol | Alt Tags | Semantic Markup | URL Canonicalization | Favicon | Broken Links | External Links | Domain Expiration | DNSSEC | DNS Blacklist | Domain Breach | Domains Blacklists | Subdomain Enumeration | Email Domain | Cookie Policy | Cookie Flags | Cookie Duration | Cookie SameSite | Ad & Tracking | FLoC Detection | Privacy Exposure | WHOIS Protection | Third-Party Requests | Third-Party Resources | Accessibility | Mobile Friendly | AMP Compatibility | Internationalization | Browser Compatibility | Content-Type Headers | CMS Detection | Client-Side Rendering | Deprecated Libraries |
|---------|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
audiolibri.org | 🟠 (16 days left) | 🟢 | 🔴 | 🔴 | 🔴 | 🟡 | 🟢 | ('🔴', 0) | 🔴 | ⚪ | ⚪ | 🟢 | 🟢 | 🔴 | 🔴 | 🟢 | 🟢 | 🔴 | 🔴 | ⚪ | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🔴 | 🟢 (333 days left) | ⚪ | 🔴 | 🟢 | 🟢 | ('🟢', []) | ⚪ | 🔴 | 🟢 | 🟢 | 🟢 | 🟢 | 🔴 | 🔴 | 🟢 | 🟢 | 🟢 | ⚪ | ⚪ | 🔴 | 🟡 | 🟢 | 🟢 | 🟢 (Magento) | 🟠 | 🟢 |
example.com | 🟢 (227 days left) | 🟢 | 🔴 | 🔴 | 🔴 | 🟢 | 🟢 | ('🟢', 0) | 🔴 | ⚪ | ⚪ | 🟢 | 🟢 | 🔴 | ⚪ | 🔴 | 🟢 | 🔴 | 🔴 | ⚪ | 🔴 | 🟢 | 🔴 | 🔴 | 🔴 | 🟢 | 🟢 | 🟡 (71 days left) | ⚪ | 🔴 | 🟢 | 🟢 | ('🟠', ['https://www.example.com']) | ⚪ | 🔴 | 🟢 | 🟢 | 🟢 | 🟢 | 🔴 | 🟢 | 🟢 | 🟢 | 🟢 | ⚪ | ⚪ | 🔴 | ⚪ | 🟢 | 🔴 | 🔴 | 🟢 | 🟢 |
