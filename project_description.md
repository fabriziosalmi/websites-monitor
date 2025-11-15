## Project Description

Website Monitor is a comprehensive website monitoring framework designed to continuously monitor various aspects of websites including security, performance, SEO compliance, and accessibility. 

### Key Features

- **Automated Monitoring**: Runs scheduled checks via GitHub Actions (daily by default)
- **Web Interface**: Interactive HTML interface for real-time testing and analysis
- **REST API**: Full-featured API for integration with other tools and services
- **Comprehensive Checks**: 53+ different checks across 7 categories
- **Multiple Deployment Options**: Local, Docker, or GitHub Actions
- **Detailed Reporting**: Automatic markdown report generation with results

### Use Cases

- **Website Health Monitoring**: Track the status and health of multiple websites
- **Security Auditing**: Identify security issues like missing SSL, weak headers, or vulnerabilities
- **Performance Tracking**: Monitor load times, PageSpeed scores, and optimization opportunities
- **SEO Compliance**: Ensure proper sitemaps, robots.txt, meta tags, and structured data
- **Accessibility Testing**: Verify WCAG compliance and mobile-friendliness
- **DevOps Integration**: Integrate with CI/CD pipelines for continuous monitoring

### Architecture

The project is built with Python and uses:
- **FastAPI**: For the web interface and REST API
- **Selenium**: For browser-based checks
- **Multiple specialized libraries**: For DNS, SSL, and other specific checks
- **Docker**: For containerized deployment
- **GitHub Actions**: For automated scheduled monitoring

### Project Status

![Static Badge](https://img.shields.io/badge/project_status-active-green?style=for-the-badge&logo=github)

The project is actively maintained and welcomes contributions. See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute.
