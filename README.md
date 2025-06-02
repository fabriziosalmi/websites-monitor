# Website Monitor

[![GitHub Workflow Status](https://github.com/fabriziosalmi/websites-monitor/actions/workflows/create-report.yml/badge.svg)](https://github.com/fabriziosalmi/websites-monitor/actions/workflows/create-report.yml)

This repository provides a framework to monitor the health and security of your websites, automatically generating a detailed report in markdown format on a daily basis. It performs various checks, including domain status, SSL certificate validity, security headers, and performance metrics, helping you keep your online presence secure and optimized.

## Screenshot

![screenshot](https://github.com/fabriziosalmi/websites-monitor/blob/main/screenshot.png?raw=true)

## Features

-   **Automated Daily Checks:** Runs daily using GitHub Actions.
-   **Comprehensive Analysis:** Performs a range of checks, including:
    -   Domain breach detection
    -   Domain expiration check
    -   SSL certificate validation
    -   DNS blacklist check
    -   HSTS header check
    -   XSS protection check
    -   Redirect chain check
    -   PageSpeed performance score
    -   Website load time
    -   Rate limiting check
    -   CDN detection
    -   Brotli compression check
    -   Deprecated libraries check
    -   Client-side rendering check
    -    Mixed content check
    -   Content-Type check
    -    Internationalization check
    -   FLoC check
    -    AMP check
    -   Robots.txt check
    -   Sitemap check
    -   Favicon check
    -   Alt tag check
    -   Open Graph check
    -   Semantic Markup check
    -   Ad Tracking check
    -   WHOIS privacy check
    -   Privacy exposure check
-   **Clear Report:** Generates a markdown-formatted report with results in a table, easily viewable on GitHub.
-   **Customizable:** Easily extendable to incorporate new checks or modify existing ones.

## How to Use

### Initial Setup

1.  **Fork This Repository:** Start by forking this repository to your GitHub account.
2.  **Configure Websites:**
    *   Edit the `config.yaml` file.
    *   Add the websites you want to monitor, one per line, under the `websites:` section.
        ```yaml
        websites:
          - audiolibri.org
          - example.com
        ```
3.  **Enable GitHub Actions (If Not Already Enabled):**
    *   Navigate to the "Actions" tab in your repository.
    *   If GitHub Actions are not enabled, enable them for your forked repository, and make sure you give write permissions.
4.  **Set the PageSpeed API Key Secret:**
    *   Obtain a Google PageSpeed Insights API key if you want to use the PageSpeed test.
    *   Navigate to "Settings" -> "Secrets and variables" -> "Actions" in your GitHub repository.
    *   Add a new repository secret named `PAGESPEED_API_KEY` and paste your API key as the value.
5.  **Create the `report_template.md` File:**
    *   Create a new file called `report_template.md` in the root of your repository if it doesn't exist.
    *   Add a default template to generate the report, for example:
    ```markdown
    # Websites Monitor
    ```
6.  **Commit All Changes:**
    *   Commit and push the changes to your forked repository to trigger the initial report generation.

### How the Monitoring Works

-   **Daily Execution:** The `create-report.yml` GitHub Action workflow is scheduled to run daily.
-   **Website Checks:** The workflow executes the `main.py` script, which performs all the checks on the websites specified in `config.yaml`.
-   **Report Generation:** The `main.py` script automatically generates the report in the `README.md` file using the `report_template.md` as a base.
-   **Automatic Updates:** The `README.md` file will be automatically updated with the latest check results after each successful run of the workflow.

## Configuration Options

The `config.yaml` file allows for various configurations:

-   `websites`: List of URLs to monitor.
-   `output_file`: The output filename of the generated report, defaults to `README.md`.
-   `max_workers`: Number of concurrent tasks when performing the checks.
-   `timeout`: Default timeout in seconds for the checks.
-   `report_template`: The filename of the report template, defaults to `report_template.md`
-   `github_workflow_badge`: The GitHub workflow badge url
-    `pagespeed_api_key`: The Google PageSpeed Insights API key (set as a GitHub Secret).

## Customizing Checks

You can modify existing checks or add new ones by editing the files in the `checks` directory and then adding the check to the `WebsiteMonitor` class in `main.py`. Ensure your new check functions follow the same format, returning an emoji indicating status (🟢, 🔴, or ⚪).

## Understanding the Output

The generated report in `README.md` includes a table with a row for each website, and the results for each check in each column.

-  🟢: The check is successful.
-  🔴: The check failed.
-  🟡: The check returned a warning or requires attention.
-  ⚪: An error occurred during the check, or the check was not completed.

## Support

For any issues or suggestions regarding this project, feel free to open an issue on GitHub.

---





This report was automatically generated on 2025-06-02 23:24:19 UTC.

| Website | SSL Certificate | SSL Cipher Strength | Security Headers | HSTS | XSS Protection | CORS Headers | Mixed Content | Subresource Integrity | Rate Limiting | Data Leakage | Pagespeed | Website Load Time | Server Response Time | Brotli Compression | Asset Minification | CDN | Redirect Chains | Redirects | Sitemap | Robots.txt | Open Graph Protocol | Alt Tags | Semantic Markup | URL Canonicalization | Favicon | Broken Links | External Links | Domain Expiration | DNSSEC | DNS Blacklist | Domain Breach | Domains Blacklists | Subdomain Enumeration | Email Domain | Cookie Policy | Cookie Flags | Cookie Duration | Cookie SameSite | Ad & Tracking | FLoC Detection | Privacy Exposure | WHOIS Protection | Third-Party Requests | Third-Party Resources | Accessibility | Mobile Friendly | AMP Compatibility | Internationalization | Browser Compatibility | Content-Type Headers | CMS Detection | Client-Side Rendering | Deprecated Libraries |
|---------|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
audiolibri.org | 🟠 (16 days left) | 🟢 | 🔴 | 🔴 | 🔴 | 🟡 | 🟢 | ('🔴', 0) | 🔴 | ⚪ | ⚪ | 🟢 | 🟢 | 🔴 | 🔴 | 🟢 | 🟢 | 🔴 | 🔴 | ⚪ | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🔴 | 🟢 (333 days left) | ⚪ | 🔴 | 🟢 | 🟢 | ('🟢', []) | ⚪ | 🔴 | 🟢 | 🟢 | 🟢 | 🟢 | 🔴 | 🔴 | 🟢 | 🟢 | 🟢 | ⚪ | ⚪ | 🔴 | 🟡 | 🟢 | 🟢 | 🟢 (Magento) | 🟠 | 🟢 |
example.com | 🟢 (227 days left) | 🟢 | 🔴 | 🔴 | 🔴 | 🟢 | 🟢 | ('🟢', 0) | 🔴 | ⚪ | ⚪ | 🟢 | 🟢 | 🔴 | ⚪ | 🔴 | 🟢 | 🔴 | 🔴 | ⚪ | 🔴 | 🟢 | 🔴 | 🔴 | 🔴 | 🟢 | 🟢 | 🟡 (71 days left) | ⚪ | 🔴 | 🟢 | 🟢 | ('🟠', ['https://www.example.com']) | ⚪ | 🔴 | 🟢 | 🟢 | 🟢 | 🟢 | 🔴 | 🟢 | 🟢 | 🟢 | 🟢 | ⚪ | ⚪ | 🔴 | ⚪ | 🟢 | 🔴 | 🔴 | 🟢 | 🟢 |
