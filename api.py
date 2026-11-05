"""
FastAPI web API for the Website Monitor project.
Provides REST endpoints to run website checks and retrieve results.
Includes individual endpoints for all 53+ security, performance, and compliance checks.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Path
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl, Field, field_validator
from urllib.parse import urlsplit
from typing import List, Optional, Dict, Any, Union
import asyncio
import logging
import threading
from datetime import datetime
import uvicorn
import importlib
import inspect
import os

from main import WebsiteMonitor, Config, load_config, generate_report

# Import ALL check functions dynamically
CHECK_MODULES = {
    'accessibility': 'checks.check_accessibility',
    'ad_and_tracking': 'checks.check_ad_and_tracking', 
    'alt_tags': 'checks.check_alt_tags',
    'amp_compatibility': 'checks.check_amp_compatibility',
    'asset_minification': 'checks.check_asset_minification',
    'broken_links': 'checks.check_broken_links',
    'brotli_compression': 'checks.check_brotli_compression',
    'browser_compatibility': 'checks.check_browser_compatibility',
    'cdn': 'checks.check_cdn',
    'clientside_rendering': 'checks.check_clientside_rendering',
    'cms_used': 'checks.check_cms_used',
    'content_type_headers': 'checks.check_content_type_headers',
    'cookie_duration': 'checks.check_cookie_duration',
    'cookie_flags': 'checks.check_cookie_flags',
    'cookie_policy': 'checks.check_cookie_policy',
    'cookie_samesite_attribute': 'checks.check_cookie_samesite_attribute',
    'cors_headers': 'checks.check_cors_headers',
    'data_leakage': 'checks.check_data_leakage',
    'deprecated_libraries': 'checks.check_deprecated_libraries',
    'dns_blacklist': 'checks.check_dns_blacklist',
    'dnssec': 'checks.check_dnssec',
    'domain_breach': 'checks.check_domain_breach',
    'domain_expiration': 'checks.check_domain_expiration',
    'domainsblacklists_blacklist': 'checks.check_domainsblacklists_blacklist',
    'email_domain': 'checks.check_email_domain',
    'external_links': 'checks.check_external_links',
    'favicon': 'checks.check_favicon',
    'floc': 'checks.check_floc',
    'hsts': 'checks.check_hsts',
    'internationalization': 'checks.check_internationalization',
    'mixed_content': 'checks.check_mixed_content',
    'mobile_friendly': 'checks.check_mobile_friendly',
    'open_graph_protocol': 'checks.check_open_graph_protocol',
    'pagespeed_performances': 'checks.check_pagespeed_performances',
    'privacy_exposure': 'checks.check_privacy_exposure',
    'privacy_protected_whois': 'checks.check_privacy_protected_whois',
    'rate_limiting': 'checks.check_rate_limiting',
    'redirect_chains': 'checks.check_redirect_chains',
    'redirects': 'checks.check_redirects',
    'robot_txt': 'checks.check_robot_txt',
    'security_headers': 'checks.check_security_headers',
    'semantic_markup': 'checks.check_semantic_markup',
    'server_response_time': 'checks.check_server_response_time',
    'sitemap': 'checks.check_sitemap',
    'ssl_cert': 'checks.check_ssl_cert',
    'ssl_cipher_strength': 'checks.check_ssl_cipher_strength',
    'subdomain_enumeration': 'checks.check_subdomain_enumeration',
    'subresource_integrity': 'checks.check_subresource_integrity',
    'third_party_requests': 'checks.check_third_party_requests',
    'third_party_resources': 'checks.check_third_party_resources',
    'url_canonicalization': 'checks.check_url_canonicalization',
    'website_load_time': 'checks.check_website_load_time',
    'xss_protection': 'checks.check_xss_protection',
}

# Category of each check, as the web UI groups them (tests/test_ui_catalog.py
# keeps the two in step).
CHECK_CATEGORIES = {
    "ssl_cert": "security",
    "ssl_cipher_strength": "security",
    "security_headers": "security",
    "hsts": "security",
    "xss_protection": "security",
    "cors_headers": "security",
    "mixed_content": "security",
    "subresource_integrity": "security",
    "rate_limiting": "security",
    "data_leakage": "security",
    "pagespeed_performances": "performance",
    "website_load_time": "performance",
    "server_response_time": "performance",
    "brotli_compression": "performance",
    "asset_minification": "performance",
    "cdn": "performance",
    "redirect_chains": "performance",
    "redirects": "performance",
    "sitemap": "seo",
    "robot_txt": "seo",
    "open_graph_protocol": "seo",
    "alt_tags": "seo",
    "semantic_markup": "seo",
    "url_canonicalization": "seo",
    "favicon": "seo",
    "broken_links": "seo",
    "external_links": "seo",
    "domain_expiration": "domain",
    "dnssec": "domain",
    "dns_blacklist": "domain",
    "domain_breach": "domain",
    "domainsblacklists_blacklist": "domain",
    "subdomain_enumeration": "domain",
    "email_domain": "domain",
    "cookie_policy": "privacy",
    "cookie_flags": "privacy",
    "cookie_duration": "privacy",
    "cookie_samesite_attribute": "privacy",
    "ad_and_tracking": "privacy",
    "floc": "privacy",
    "privacy_exposure": "privacy",
    "privacy_protected_whois": "privacy",
    "third_party_requests": "privacy",
    "third_party_resources": "privacy",
    "accessibility": "accessibility",
    "mobile_friendly": "accessibility",
    "amp_compatibility": "accessibility",
    "internationalization": "accessibility",
    "browser_compatibility": "accessibility",
    "content_type_headers": "technical",
    "cms_used": "technical",
    "clientside_rendering": "technical",
    "deprecated_libraries": "technical",
}

# Load all check functions
CHECK_FUNCTIONS = {}
for check_name, module_path in CHECK_MODULES.items():
    try:
        module = importlib.import_module(module_path)
        function_name = f"check_{check_name}"
        if hasattr(module, function_name):
            CHECK_FUNCTIONS[check_name] = getattr(module, function_name)
    except ImportError as e:
        logging.warning(f"Could not import {module_path}: {e}")
        continue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Website Monitor API",
    description=(
        "Runs security, performance, SEO, privacy and accessibility checks "
        "against a website. Each check returns a verdict: pass, warning, fail, "
        "or no verdict when it could not run. GET /checks lists them; "
        "POST /monitor/single runs a selection against one site, and "
        "GET /check/{name} runs a single check."
    ),
    version="1.3.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def normalize_website(value: str) -> str:
    """
    The host the checks run against: "https://Example.com:8443/path" and
    "example.com" both give "example.com". Each check builds its own URLs
    from a bare host; given a URL, rate_limiting asked for
    https://https://audiolibri.org/.
    """
    raw = (value or "").strip()
    if not raw:
        raise ValueError("website is empty")
    host = urlsplit(raw if "://" in raw else f"//{raw}").hostname
    if not host or any(c.isspace() for c in host):
        raise ValueError(f"not a domain or URL: {raw!r}")
    return host.rstrip(".").lower()


# Pydantic models for API
class WebsiteRequest(BaseModel):
    websites: List[str] = Field(..., description="List of website URLs or domains to monitor", example=["example.com", "google.com"])
    timeout: Optional[int] = Field(30, description="Timeout in seconds for each check", ge=5, le=300)
    pagespeed_api_key: Optional[str] = Field(None, description="Optional Google PageSpeed Insights API key")

    @field_validator("websites")
    @classmethod
    def hosts_only(cls, values: List[str]) -> List[str]:
        return [normalize_website(v) for v in values]

class SingleCheckRequest(BaseModel):
    website: str = Field(..., description="Website URL or domain to check", example="example.com")
    timeout: Optional[int] = Field(30, description="Timeout in seconds", ge=5, le=300)
    pagespeed_api_key: Optional[str] = Field(None, description="Optional Google PageSpeed Insights API key")

    @field_validator("website")
    @classmethod
    def host_only(cls, value: str) -> str:
        return normalize_website(value)

class CustomMonitorRequest(BaseModel):
    website: str = Field(..., description="Website URL or domain to monitor", example="example.com")
    checks: List[str] = Field(..., description="List of check names to run", example=["ssl_cert", "security_headers"])
    timeout: Optional[int] = Field(30, description="Timeout in seconds for each check", ge=5, le=300)
    pagespeed_api_key: Optional[str] = Field(None, description="Optional Google PageSpeed Insights API key")

    @field_validator("website")
    @classmethod
    def host_only(cls, value: str) -> str:
        return normalize_website(value)

class CheckResult(BaseModel):
    check_name: str = Field(..., description="Name of the check performed")
    website: str = Field(..., description="Website that was checked") 
    result: str = Field(..., description="Check result (🟢 pass, 🔴 fail, ⚪ error, 🟡 warning)")
    status: str = Field(..., description="Execution status", example="completed")
    error: Optional[str] = Field(None, description="Error message if check failed")
    timestamp: datetime = Field(..., description="When the check was performed")

class CheckInfo(BaseModel):
    name: str = Field(..., description="Check name")
    description: str = Field(..., description="Check description")
    category: str = Field(..., description="Check category (security, performance, seo, etc.)")
    enabled: bool = Field(..., description="Whether check is enabled")
    timeout: Optional[int] = Field(None, description="Default timeout for this check")
    endpoint: str = Field(..., description="API endpoint for this individual check")

class MonitorResponse(BaseModel):
    success: bool = Field(..., description="Whether monitoring completed successfully")
    message: str = Field(..., description="Summary message")
    results: List[Dict[str, Any]] = Field(..., description="Detailed check results")
    execution_time: float = Field(..., description="Total execution time in seconds")
    timestamp: datetime = Field(..., description="When monitoring was performed")
    websites_checked: int = Field(..., description="Number of websites monitored")
    checks_performed: int = Field(..., description="Total number of checks performed")

class HealthResponse(BaseModel):
    status: str = Field(..., description="API health status", example="healthy")
    version: str = Field(..., description="API version", example="1.0.0")
    timestamp: datetime = Field(..., description="Current server time")
    total_checks_available: int = Field(..., description="Number of available checks")
    config_loaded: bool = Field(..., description="Whether default config was loaded successfully")

class ReportRequest(BaseModel):
    websites: List[str] = Field(..., description="Websites to include in report")
    output_format: str = Field("markdown", description="Report format", pattern="^(markdown|json|html)$")
    include_timestamp: bool = Field(True, description="Whether to include timestamp in report")
    timeout: Optional[int] = Field(30, description="Timeout for checks")

# Global variable to store the default config
default_config = None

# Mount static files for custom docs
if not os.path.exists("docs"):
    os.makedirs("docs")
app.mount("/docs", StaticFiles(directory="docs", html=True), name="docs")

@app.on_event("startup")
async def startup_event():
    """Load default configuration on startup."""
    global default_config
    try:
        default_config = load_config()
        logger.info(f"API started successfully with default configuration for {len(default_config.websites)} websites")
        logger.info(f"Loaded {len(CHECK_FUNCTIONS)} check functions")
    except Exception as e:
        logger.error(f"Failed to load default configuration: {e}")
        # Create a minimal config as fallback
        default_config = Config(websites=["example.com"])

    # The domain blacklist takes 20-30 s to download: fetch it now, not
    # inside the first scan, where it would hit the check timeout.
    from checks.check_domainsblacklists_blacklist import prefetch_blacklist
    threading.Thread(target=prefetch_blacklist, daemon=True).start()

@app.get("/", tags=["Root"])
async def root():
    """
    Redirect to the web interface under /docs/.

    The page loads its stylesheet, script and fonts by relative path, and
    those only exist under the /docs mount: served at /, every one of them
    was a 404.
    """
    html_file_path = os.path.join(os.path.dirname(__file__), "docs", "index.html")
    if not os.path.exists(html_file_path):
        raise HTTPException(status_code=404, detail="Frontend interface not found")
    return RedirectResponse(url="/docs/", status_code=307)

@app.get("/api", include_in_schema=False)
async def api_landing():
    """The interactive API reference lives at /api/docs."""
    return RedirectResponse(url="/api/docs", status_code=307)

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    ## Health Check
    
    Get the current health status of the API, including:
    - Service status
    - Available checks count
    - Configuration status
    - Current server time
    """
    global default_config
    return HealthResponse(
        status="healthy",
        version=app.version,
        timestamp=datetime.now(),
        total_checks_available=len(CHECK_FUNCTIONS),
        config_loaded=default_config is not None
    )

@app.get("/checks", tags=["Checks"])
async def list_checks():
    """
    List the checks this API runs: the ids that POST /monitor/single and
    GET /check/{name} accept, with their category and description.

    It used to list each check twice, under its id and under the name
    main.py gives it, and filed most of them under "other".
    """
    all_checks = []
    for check_id, check_func in sorted(CHECK_FUNCTIONS.items()):
        all_checks.append({
            "name": check_id.replace("_", " ").title(),
            "slug": check_id,
            "enabled": True,
            "timeout": None,
            "description": inspect.getdoc(check_func) or "",
            "category": CHECK_CATEGORIES.get(check_id, "technical"),
            "endpoint": f"/check/{check_id}",
        })

    checks_by_category = {}
    for check in all_checks:
        checks_by_category.setdefault(check["category"], []).append(check)

    return {
        "total_checks": len(all_checks),
        "categories": list(checks_by_category),
        "checks_by_category": checks_by_category,
        "all_checks": all_checks,
    }

@app.post("/monitor", response_model=MonitorResponse, tags=["Monitoring"])
async def monitor_websites(request: WebsiteRequest):
    """
    ## Comprehensive Website Monitoring
    
    Run all available security, performance, and compliance checks on multiple websites.
    
    **Features:**
    - 50+ specialized checks per website
    - Parallel execution for optimal performance
    - Detailed results with status indicators
    - Custom timeout configuration
    - PageSpeed Insights integration (with API key)
    
    **Result Indicators:**
    - 🟢 Check passed
    - 🔴 Check failed  
    - 🟡 Check warning/partial
    - ⚪ Check error/timeout
    """
    start_time = datetime.now()
    
    try:
        # Create config from request
        config = Config(
            websites=request.websites,
            timeout=request.timeout or 30,
            pagespeed_api_key=request.pagespeed_api_key
        )
        
        monitor = WebsiteMonitor(config)
        
        # Run all checks
        results = []
        total_checks = 0
        
        for check in monitor.check_functions:
            check_results = []
            for website in config.websites:
                try:
                    result = await check.execute(website, config, config.timeout)
                    check_results.append({
                        "website": website,
                        "result": result,
                        "status": "completed"
                    })
                    total_checks += 1
                except Exception as e:
                    logger.error(f"Check {check.name} failed for {website}: {e}")
                    check_results.append({
                        "website": website,
                        "result": "⚪",
                        "status": "error",
                        "error": str(e)
                    })
                    total_checks += 1
            
            results.append({
                "check_name": check.name,
                "results": check_results
            })
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        return MonitorResponse(
            success=True,
            message=f"Monitoring completed successfully",
            results=results,
            execution_time=execution_time,
            timestamp=end_time,
            websites_checked=len(request.websites),
            checks_performed=total_checks
        )
        
    except Exception as e:
        logger.error(f"Monitoring failed: {e}")
        raise HTTPException(status_code=500, detail=f"Monitoring failed: {str(e)}")

@app.get("/monitor/single", tags=["Monitoring"])
async def monitor_single_website(
    website: str = Query(..., description="Website URL or domain to monitor", example="example.com"),
    timeout: Optional[int] = Query(30, description="Timeout in seconds for each check", ge=5, le=300),
    pagespeed_api_key: Optional[str] = Query(None, description="Optional PageSpeed Insights API key")
):
    """
    ## Single Website Monitoring
    
    Convenient endpoint for running all checks on a single website.
    Perfect for testing and quick analysis.
    
    **Use Cases:**
    - Quick website health check
    - Testing specific domains
    - Development and debugging
    - Integration testing
    """
    request = WebsiteRequest(
        websites=[website],
        timeout=timeout,
        pagespeed_api_key=pagespeed_api_key
    )
    
    return await monitor_websites(request)

@app.post("/monitor/single", tags=["Monitoring"])
async def monitor_single_website_custom(request: CustomMonitorRequest):
    """
    ## Custom Single Website Monitoring
    
    Run selected checks on a single website with custom check selection.
    Perfect for targeted analysis and custom workflows.
    
    **Features:**
    - Custom check selection from 50+ available checks
    - Single website focus for faster analysis
    - Custom timeout configuration
    - Detailed results for selected checks only
    """
    start_time = datetime.now()

    try:
        config = Config(
            websites=[request.website],
            timeout=request.timeout or 30,
            pagespeed_api_key=request.pagespeed_api_key
        )
        monitor = WebsiteMonitor(config)
        monitor_checks = {
            check.name.lower().replace(" ", "_").replace("-", "_"): check
            for check in monitor.check_functions
        }

        # Each requested check runs once, in request order. A CHECK_FUNCTIONS
        # key and a WebsiteMonitor slug can name the same function (hsts, cdn,
        # security_headers, ...): the CHECK_FUNCTIONS key wins, so asking for
        # five checks no longer runs nine.
        results = []
        for check_id in dict.fromkeys(request.checks):
            if check_id in CHECK_FUNCTIONS:
                check_name = check_id.replace("_", " ").title()
                pending = _run_individual_check(check_id, request.website, config)
            elif check_id in monitor_checks:
                check = monitor_checks[check_id]
                check_name = check.name
                pending = check.execute(request.website, config, config.timeout)
            else:
                results.append({
                    "check_id": check_id,
                    "check_name": check_id,
                    "website": request.website,
                    "result": "⚪",
                    "status": "error",
                    "error": "Unknown check",
                    "timestamp": datetime.now()
                })
                continue

            try:
                result = await asyncio.wait_for(pending, timeout=config.timeout)
                results.append({
                    "check_id": check_id,
                    "check_name": check_name,
                    "website": request.website,
                    "result": result,
                    "status": "completed",
                    "timestamp": datetime.now()
                })
            except asyncio.TimeoutError:
                logger.warning(f"Check {check_id} timed out for {request.website}")
                results.append({
                    "check_id": check_id,
                    "check_name": check_name,
                    "website": request.website,
                    "result": "⚪",
                    "status": "error",
                    "error": f"Timed out after {config.timeout}s",
                    "timestamp": datetime.now()
                })
            except Exception as e:
                logger.error(f"Check {check_id} failed for {request.website}: {e}")
                results.append({
                    "check_id": check_id,
                    "check_name": check_name,
                    "website": request.website,
                    "result": "⚪",
                    "status": "error",
                    "error": str(e) or type(e).__name__,
                    "timestamp": datetime.now()
                })

        end_time = datetime.now()

        return MonitorResponse(
            success=True,
            message="Custom monitoring completed successfully",
            results=results,
            execution_time=(end_time - start_time).total_seconds(),
            timestamp=end_time,
            websites_checked=1,
            checks_performed=len(results)
        )

    except Exception as e:
        logger.error(f"Custom monitoring failed: {e}")
        raise HTTPException(status_code=500, detail=f"Custom monitoring failed: {str(e)}")


async def _run_individual_check(check_id: str, website: str, config: Config):
    """Run one CHECK_FUNCTIONS entry with the arguments its signature needs."""
    check_func = CHECK_FUNCTIONS[check_id]
    if check_id == "pagespeed_performances":
        args = (website, config.pagespeed_api_key or os.environ.get("PAGESPEED_API_KEY", ""))
    elif check_id == "rate_limiting":
        args = (website, 10)
    else:
        args = (website,)
    if asyncio.iscoroutinefunction(check_func):
        return await check_func(*args)
    return await asyncio.to_thread(check_func, *args)

# Generate individual endpoints for each check function
def create_check_endpoint(check_name: str, check_func: callable):
    async def endpoint(
        website: str = Query(..., description=f"Website URL or domain to check with {check_name}", example="example.com"),
        timeout: Optional[int] = Query(30, description="Timeout in seconds", ge=5, le=300)
    ):
        try:
            website = normalize_website(website)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        try:
            start_time = datetime.now()
            # Sync checks run in a worker thread: called inline they blocked
            # the event loop, /health included, for as long as they took.
            config = Config(websites=[website], timeout=timeout or 30)
            result = await asyncio.wait_for(_run_individual_check(check_name, website, config), timeout)

            end_time = datetime.now()
            
            return {
                "check_name": check_name.replace("_", " ").title(),
                "website": website,
                "result": result,
                "timestamp": end_time,
                "status": "completed", 
                "execution_time": (end_time - start_time).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"Check {check_name} failed for {website}: {e}")
            raise HTTPException(status_code=500, detail=f"Check failed: {str(e)}")
    
    return endpoint

# Add individual endpoints for each check
for check_name, check_func in CHECK_FUNCTIONS.items():
    endpoint_func = create_check_endpoint(check_name, check_func)
    endpoint_func.__name__ = f"check_{check_name}"
    
    # inspect.getdoc strips indentation the same way on every Python
    # version: pasted raw into an indented string, the docstring gave a
    # different description on 3.11 than on 3.13, which dedents at compile
    # time.
    description = inspect.getdoc(check_func) or f"Run the {check_name} check."
    category = CHECK_CATEGORIES.get(check_name, "technical").title()
    endpoint_func.__doc__ = (
        f"## {check_name.replace('_', ' ').title()} Check\n\n{description}\n\n**Category:** {category}"
    )

    app.get(f"/check/{check_name}", tags=["Individual Checks"])(endpoint_func)

# Background task management
background_tasks = {}

@app.post("/monitor/async", tags=["Async Monitoring"])
async def monitor_websites_async(request: WebsiteRequest, background_tasks: BackgroundTasks):
    """
    ## Asynchronous Website Monitoring
    
    Start monitoring checks in the background and return immediately with a task ID.
    Useful for large batch jobs or when you don't want to wait for completion.
    
    **Workflow:**
    1. Submit monitoring request
    2. Receive task ID immediately
    3. Use task ID to check status via `/monitor/async/{task_id}`
    4. Retrieve results when complete
    """
    import uuid
    task_id = str(uuid.uuid4())
    
    background_tasks.add_task(run_monitoring_task, task_id, request)
    
    return {
        "task_id": task_id,
        "status": "started",
        "message": f"Monitoring task started for {len(request.websites)} websites",
        "timestamp": datetime.now(),
        "check_status_url": f"/monitor/async/{task_id}"
    }

async def run_monitoring_task(task_id: str, request: WebsiteRequest):
    """Background task to run monitoring."""
    try:
        # Store task status
        background_tasks[task_id] = {
            "status": "running", 
            "started_at": datetime.now(),
            "websites": request.websites,
            "progress": 0
        }
        
        # Run the monitoring
        result = await monitor_websites(request)
        
        # Store the result
        background_tasks[task_id] = {
            "status": "completed", 
            "started_at": background_tasks[task_id]["started_at"],
            "completed_at": datetime.now(),
            "websites": request.websites,
            "progress": 100,
            "result": result
        }
        
    except Exception as e:
        background_tasks[task_id] = {
            "status": "failed", 
            "started_at": background_tasks[task_id]["started_at"],
            "failed_at": datetime.now(),
            "websites": request.websites,
            "progress": 0,
            "error": str(e)
        }

@app.get("/monitor/async/{task_id}", tags=["Async Monitoring"])
async def get_monitoring_task_status(task_id: str = Path(..., description="Task ID returned from async monitoring request")):
    """
    ## Check Async Task Status
    
    Get the current status of a background monitoring task.
    
    **Status Values:**
    - `running`: Task is currently executing
    - `completed`: Task finished successfully
    - `failed`: Task encountered an error
    """
    if task_id not in background_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return background_tasks[task_id]

@app.post("/generate-report", tags=["Reports"])
async def generate_monitoring_report(request: ReportRequest):
    """
    ## Generate Monitoring Report
    
    Create a comprehensive monitoring report for websites.
    Supports multiple output formats including Markdown, JSON, and HTML.
    
    **Features:**
    - Multi-format output (Markdown, JSON, HTML)
    - Comprehensive check results
    - Timestamp and metadata inclusion
    - Customizable website selection
    """
    try:
        # Create config for report generation
        config = Config(
            websites=request.websites,
            timeout=request.timeout or 30,
            output_file="api_generated_report.md" if request.output_format == "markdown" else f"api_generated_report.{request.output_format}"
        )
        
        # Run monitoring
        monitor_request = WebsiteRequest(websites=request.websites, timeout=request.timeout)
        monitor_result = await monitor_websites(monitor_request)
        
        if request.output_format == "json":
            return {
                "format": "json",
                "timestamp": datetime.now(),
                "report_data": monitor_result,
                "websites_count": len(request.websites),
                "generation_time": datetime.now()
            }
        elif request.output_format == "markdown":
            # Generate markdown report using existing function
            check_results = []
            for result_group in monitor_result.results:
                results_list = []
                for website_result in result_group["results"]:
                    results_list.append(website_result["result"])
                check_results.append((result_group["check_name"], results_list))
            
            generate_report(config, check_results)
            
            # Read the generated file
            with open(config.output_file, "r") as f:
                report_content = f.read()
            
            return {
                "format": "markdown",
                "timestamp": datetime.now(),
                "report_content": report_content,
                "websites_count": len(request.websites),
                "generation_time": datetime.now()
            }
        else:
            # HTML format
            html_content = _generate_html_report(monitor_result, request)
            return {
                "format": "html",
                "timestamp": datetime.now(), 
                "report_content": html_content,
                "websites_count": len(request.websites),
                "generation_time": datetime.now()
            }
            
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

def _generate_html_report(monitor_result: MonitorResponse, request: ReportRequest) -> str:
    """Generate HTML report from monitoring results."""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Website Monitor Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .pass {{ color: green; }}
            .fail {{ color: red; }}
            .warning {{ color: orange; }}
            .error {{ color: gray; }}
        </style>
    </head>
    <body>
        <h1>Website Security & Performance Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        <p><strong>Websites Checked:</strong> {len(request.websites)}</p>
        <p><strong>Execution Time:</strong> {monitor_result.execution_time:.2f} seconds</p>
        
        <table>
            <thead>
                <tr>
                    <th>Check</th>
                    {' '.join([f'<th>{website}</th>' for website in request.websites])}
                </tr>
            </thead>
            <tbody>
    """
    
    for result_group in monitor_result.results:
        html += f"<tr><td>{result_group['check_name']}</td>"
        for website_result in result_group["results"]:
            result = website_result["result"]
            css_class = "pass" if result == "🟢" else "fail" if result == "🔴" else "warning" if result == "🟡" else "error"
            html += f'<td class="{css_class}">{result}</td>'
        html += "</tr>"
    
    html += """
            </tbody>
        </table>
    </body>
    </html>
    """
    
    return html

if __name__ == "__main__":
    print("🚀 Starting Website Monitor API...")
    print(f"📊 {len(CHECK_FUNCTIONS)} check functions loaded")
    print("📚 API Documentation will be available at:")
    print("   - http://localhost:8000/api/docs (Swagger UI)")
    print("   - http://localhost:8000/api/redoc (ReDoc)")
    print("   - http://localhost:8000/ (UI)")
    # Reloading restarts the server whenever a file under the app changes,
    # and drops every request in flight: development only.
    reload = os.environ.get("API_RELOAD", "").lower() in ("1", "true", "yes")
    uvicorn.run("api:app", host=os.environ.get("API_HOST", "0.0.0.0"),
                port=int(os.environ.get("API_PORT", "8000")), reload=reload)
