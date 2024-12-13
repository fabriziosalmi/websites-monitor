# Standard library imports
from datetime import datetime
import logging
from typing import List, Tuple, Callable, Optional
from pathlib import Path
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import json

# Third-party imports
import yaml
from dataclasses import dataclass

# Import all check functions
from checks.check_domain_breach import check_domain_breach
from checks.check_domain_expiration import check_domain_expiration
from checks.check_ssl_cert import check_ssl_cert
from checks.check_dns_blacklist import check_dns_blacklist
from checks.check_domainsblacklists_blacklist import check_domainsblacklists_blacklist
from checks.check_hsts import check_hsts
from checks.check_xss_protection import check_xss_protection
from checks.check_redirect_chains import check_redirect_chains
from checks.check_pagespeed_performances import check_pagespeed_performances
from checks.check_website_load_time import check_website_load_time
from checks.check_rate_limiting import check_rate_limiting
from checks.check_cdn import check_cdn
from checks.check_brotli_compression import check_brotli_compression
from checks.check_deprecated_libraries import check_deprecated_libraries
from checks.check_clientside_rendering import check_clientside_rendering
from checks.check_mixed_content import check_mixed_content
from checks.check_content_type_headers import check_content_type_headers
from checks.check_internationalization import check_internationalization
from checks.check_floc import check_floc
from checks.check_amp_compatibility import check_amp_compatibility
from checks.check_robot_txt import check_robot_txt
from checks.check_sitemap import check_sitemap
from checks.check_favicon import check_favicon
from checks.check_alt_tags import check_alt_tags
from checks.check_open_graph_protocol import check_open_graph_protocol
from checks.check_semantic_markup import check_semantic_markup
from checks.check_ad_and_tracking import check_ad_and_tracking
from checks.check_privacy_protected_whois import check_privacy_protected_whois
from checks.check_privacy_exposure import check_privacy_exposure

# Optional imports for future use (commented out)
"""
from checks.check_security_headers import check_security_headers
from checks.check_ssl_cipher_strength import check_ssl_cipher_strength
from checks.check_cors_headers import check_cors_headers
from checks.check_cookie_flags import check_cookie_flags
from checks.check_cookie_policy import check_cookie_policy
from checks.check_cookie_duration import check_cookie_duration
from checks.check_cookie_samesite_attribute import check_cookie_samesite_attribute
from checks.check_subdomain_enumeration import check_subdomain_enumeration
from checks.check_asset_minification import check_asset_minification
from checks.check_broken_links import check_broken_links
from checks.check_browser_compatibility import check_browser_compatibility
from checks.check_dnssec import check_dnssec
from checks.check_external_links import check_external_links
from checks.check_mobile_friendly import check_mobile_friendly
from checks.check_server_response_time import check_server_response_time
from checks.check_subresource_integrity import check_subresource_integrity
from checks.check_third_party_requests import check_third_party_requests
from checks.check_third_party_resources import check_third_party_resources
from checks.check_url_canonicalization import check_url_canonicalization
"""

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Config:
    """Configuration class to store all settings."""
    websites: List[str]
    output_file: str = "README.md"
    max_workers: int = 4
    timeout: int = 30
    log_file: str = "monitor.log"
    report_template: str = "report_template.md"
    github_workflow_badge: str = "https://github.com/fabriziosalmi/websites-monitor/actions/workflows/create-report.yml/badge.svg"
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Config':
        """Create a Config instance from a dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

class WebsiteMonitor:
    def __init__(self, config: Config):
        self.config = config
        self.error_log = []
        self.check_functions = self._initialize_check_functions()

    class Check:
        """Represents a single website check."""
        def __init__(self, name: str, function: Callable, enabled: bool = True, timeout: Optional[int] = None):
            self.name = name
            self.function = function
            self.enabled = enabled
            self.timeout = timeout

        async def execute(self, website: str, default_timeout: int) -> str:
            """Execute the check with timeout handling."""
            timeout = self.timeout or default_timeout
            try:
                result = await asyncio.wait_for(self.function(website), timeout)
                return result
            except asyncio.TimeoutError:
                return "🔴"  # Timeout indicator
            except Exception as e:
                logger.error(f"Check {self.name} failed for {website}: {e}")
                return "⚪"  # Error indicator

    def _initialize_check_functions(self) -> List['WebsiteMonitor.Check']:
        """Initialize the list of check functions with their names."""
        checks = [
            self.Check("Domain breach", check_domain_breach),
            self.Check("Domain Expiration", check_domain_expiration),
            self.Check("SSL Certificate", check_ssl_cert),
            self.Check("DNS Blacklists", check_dns_blacklist, timeout=45),
            self.Check("DomainsBlacklists", check_domainsblacklists_blacklist),
            self.Check("HSTS", check_hsts),
            self.Check("XSS Protection", check_xss_protection),
            self.Check("Redirect chains", check_redirect_chains),
            self.Check("Pagespeed", check_pagespeed_performances, timeout=60),
            self.Check("Load Time", check_website_load_time),
            self.Check("Rate Limiting", check_rate_limiting),
            self.Check("CDN", check_cdn),
            self.Check("Brotli", check_brotli_compression),
            self.Check("Deprecated Libraries", check_deprecated_libraries),
            self.Check("Client Rendering", check_clientside_rendering),
            self.Check("Mixed Content", check_mixed_content),
            self.Check("Content-Type", check_content_type_headers),
            self.Check("i18n", check_internationalization),
            self.Check("FLoC", check_floc),
            self.Check("AMP", check_amp_compatibility),
            self.Check("Robots.txt", check_robot_txt),
            self.Check("Sitemap", check_sitemap),
            self.Check("Favicon", check_favicon),
            self.Check("Alt Tags", check_alt_tags),
            self.Check("Open Graph", check_open_graph_protocol),
            self.Check("Semantic Markup", check_semantic_markup),
            self.Check("Ad Tracking", check_ad_and_tracking),
            self.Check("WHOIS Privacy", check_privacy_protected_whois),
            self.Check("Privacy Exposure", check_privacy_exposure),
        ]
        return [check for check in checks if check.enabled]


    def log_error(self, message: str) -> None:
        """Log errors with proper formatting and tracking."""
        self.error_log.append(message)
        logger.error(message)

    def _read_markdown_file(self, filename: str) -> str:
        """Read markdown file content with proper error handling."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"File {filename} not found. Skipping...")
            return ""
        except Exception as e:
            logger.error(f"Error reading {filename}: {e}")
            return ""

    async def check_website(self, website: str, check_name: str, check_func: Callable) -> str:
        """Execute a single check for a website with timeout."""
        try:
            result = await check_func(website)
            return result
        except Exception as e:
            error_msg = f"Error occurred with {check_name} for {website}: {e}"
            self.log_error(error_msg)
            return "⚪"

    class ReportGenerator:
        """Handles report generation and formatting."""
        def __init__(self, config: Config):
            self.config = config
        
        def _create_table_header(self, websites: List[str]) -> str:
            """Create the markdown table header."""
            headers = ["Check Type"] + websites
            header_row = "| " + " | ".join(headers) + " |"
            separator_row = "|" + "|".join(["---"] * len(headers)) + "|"
            return f"{header_row}\n{separator_row}\n"
        
        def _format_check_row(self, check_name: str, results: List[str]) -> str:
            """Format a single check row in the table."""
            return f"| {check_name} | {' | '.join(results)} |"
        
        async def generate_report(self, check_results: List[Tuple[str, List[str]]]) -> str:
            """Generate the complete monitoring report."""
            template = self._read_markdown_file(self.config.report_template)
            if not template:
                template = """# Websites Monitor
{description}
{instructions}
## Monitoring Checks
[![Create report]({badge})]({badge_link})
{table_content}
---
Last Updated: {timestamp}
"""
        
            description = self._read_markdown_file('project_description.md')
            instructions = self._read_markdown_file('usage_instructions.md')
            table_header = self._create_table_header(self.config.websites)
            table_rows = [self._format_check_row(name, results) for name, results in check_results]
        
            return template.format(
                description=description,
                instructions=instructions,
                badge=self.config.github_workflow_badge,
                badge_link=self.config.github_workflow_badge,
                table_content=table_header + "\n".join(table_rows),
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )

        def save_report(self, report_content: str) -> None:
            """Save the report to file with error handling."""
            try:
                with open(self.config.output_file, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                logger.info(f"Report successfully saved to {self.config.output_file}")
            except Exception as e:
                logger.error(f"Failed to save report: {e}")
                raise

    def save_report(self, report_content: str) -> None:
        """Save the report to file with error handling."""
        try:
            with open(self.config.output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"Report successfully saved to {self.config.output_file}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            raise

def load_config(config_file: str = 'config.yaml') -> Config:
    """Load configuration from YAML file."""
    try:
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        return Config(**config_data)
    except FileNotFoundError:
        # Fallback to default configuration
        logger.warning("Config file not found, using default configuration")
        with open('websites.txt', 'r') as f:
            websites = [line.strip() for line in f.readlines()]
        return Config(websites=websites)

class PerformanceMonitor:
    """Tracks execution time and performance metrics."""
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.check_times = {}
        
    def start(self):
        """Start monitoring."""
        self.start_time = datetime.now()
        
    def stop(self):
        """Stop monitoring."""
        self.end_time = datetime.now()
        
    def record_check(self, check_name: str, duration: float):
        """Record the duration of a single check."""
        if check_name not in self.check_times:
            self.check_times[check_name] = []
        self.check_times[check_name].append(duration)
        
    def get_summary(self) -> dict:
        """Get performance summary."""
        if not self.start_time or not self.end_time:
            return {}
            
        total_duration = (self.end_time - self.start_time).total_seconds()
        avg_check_times = {
            name: sum(times) / len(times) 
            for name, times in self.check_times.items()
        }
        
        return {
            "total_duration": total_duration,
            "average_check_times": avg_check_times,
            "slowest_check": max(avg_check_times.items(), key=lambda x: x[1]) if avg_check_times else None
        }

async def main():
    """Main execution function with performance monitoring."""
    performance_monitor = PerformanceMonitor()
    performance_monitor.start()
    try:
        # Load configuration
        config = load_config()

        # Initialize the WebsiteMonitor
        monitor = WebsiteMonitor(config)

        # Initialize the ReportGenerator
        report_generator = monitor.ReportGenerator(config)

        # Run the checks and generate the report
        check_results = []  # Collect check results
        for check in monitor.check_functions:
            results = []
            for website in config.websites:
                result = await check.execute(website, config.timeout)
                results.append(result)
            check_results.append((check.name, results))
        
        report_content = await report_generator.generate_report(check_results)

        # Save the generated report
        report_generator.save_report(report_content)

        if monitor.error_log:
            logger.warning("Completed with some errors. Check the log file for details.")
            sys.exit(1)
        logger.info("Monitoring completed successfully")

    except Exception as e:
        logger.error(f"Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

