"""
FastAPI web API for the Website Monitor project.
Provides REST endpoints to run website checks and retrieve results.
Includes individual endpoints for all 53+ security, performance, and compliance checks.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Path
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any, Union
import asyncio
import logging
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
    description="""
    ## 🔍 Comprehensive Website Security & Performance Monitor API
    
    This API provides 50+ security, performance, and compliance checks for websites including:
    
    ### 🛡️ Security Checks
    - SSL Certificate validation
    - Security headers analysis
    - XSS protection verification  
    - CORS configuration review
    - Domain breach detection
    - DNS blacklist checking
    
    ### ⚡ Performance Checks  
    - PageSpeed Insights integration
    - Load time measurement
    - CDN detection
    - Brotli compression analysis
    - Asset minification verification
    
    ### 🎯 SEO & Compliance
    - Robots.txt validation
    - Sitemap detection
    - Open Graph protocol
    - Accessibility compliance
    - Mobile-friendly testing
    
    ### 📊 Advanced Features
    - Batch monitoring of multiple websites
    - Individual check endpoints for each test
    - Async background processing
    - Report generation
    - Custom timeout configurations
    
    **Total Available Checks:** 53+
    """,
    version="1.0.0",
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

# Pydantic models for API
class WebsiteRequest(BaseModel):
    websites: List[str] = Field(..., description="List of website URLs or domains to monitor", example=["example.com", "google.com"])
    timeout: Optional[int] = Field(30, description="Timeout in seconds for each check", ge=5, le=300)
    pagespeed_api_key: Optional[str] = Field(None, description="Optional Google PageSpeed Insights API key")

class SingleCheckRequest(BaseModel):
    website: str = Field(..., description="Website URL or domain to check", example="example.com")
    timeout: Optional[int] = Field(30, description="Timeout in seconds", ge=5, le=300)
    pagespeed_api_key: Optional[str] = Field(None, description="Optional Google PageSpeed Insights API key")

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

@app.get("/", response_class=HTMLResponse, tags=["Root"])
async def root():
    """
    API landing page with navigation and quick start information.
    """
    return f"""
    <html>
        <head>
            <title>Website Monitor API</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', roboto, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; line-height: 1.6; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
                .card {{ background: #f8f9fa; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #667eea; }}
                .endpoint {{ background: #fff; padding: 15px; margin: 10px 0; border-radius: 5px; border: 1px solid #e9ecef; }}
                .badge {{ background: #28a745; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.8em; margin-left: 10px; }}
                .category {{ background: #17a2b8; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.75em; margin-right: 5px; }}
                ul {{ columns: 2; column-gap: 30px; }}
                li {{ margin-bottom: 5px; break-inside: avoid; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔍 Website Monitor API</h1>
                <p>Comprehensive website security, performance, and compliance monitoring with {len(CHECK_FUNCTIONS)} specialized checks</p>
            </div>
            
            <div class="card">
                <h2>📚 API Documentation</h2>
                <div class="endpoint">
                    <strong>🚀 Interactive API Docs (Swagger UI):</strong> <a href="/api/docs">/api/docs</a><span class="badge">Recommended</span><br>
                    <strong>📖 ReDoc Documentation:</strong> <a href="/api/redoc">/api/redoc</a><br>
                    <strong>📄 OpenAPI Schema:</strong> <a href="/api/openapi.json">/api/openapi.json</a><br>
                    <strong>📁 Custom Documentation:</strong> <a href="/docs/">/docs/</a>
                </div>
            </div>
            
            <div class="card">
                <h2>🎯 Quick Start Endpoints</h2>
                <div class="endpoint">
                    <strong>GET /health</strong> - API health and status information<br>
                    <strong>GET /checks</strong> - List all {len(CHECK_FUNCTIONS)} available checks<br>
                    <strong>POST /monitor</strong> - Run all checks on multiple websites<br>
                    <strong>GET /monitor/single</strong> - Quick single website monitoring<br>
                    <strong>POST /generate-report</strong> - Generate comprehensive reports
                </div>
            </div>

            <div class="card">
                <h2>🔧 Individual Check Endpoints</h2>
                <p>Each of our {len(CHECK_FUNCTIONS)} checks has its own dedicated endpoint:</p>
                <ul>
                    {chr(10).join([f'<li><span class="category">CHECK</span> <code>/check/{name}</code></li>' for name in sorted(CHECK_FUNCTIONS.keys())])}
                </ul>
            </div>
            
            <div class="card">
                <h2>💡 Example Usage</h2>
                <div class="endpoint">
                    <strong>Single Website Check:</strong><br>
                    <code>curl "http://localhost:8000/monitor/single?website=example.com"</code><br><br>
                    <strong>Specific Security Check:</strong><br>
                    <code>curl "http://localhost:8000/check/ssl_cert?website=example.com"</code><br><br>
                    <strong>Batch Monitoring:</strong><br>
                    <code>curl -X POST "http://localhost:8000/monitor" -H "Content-Type: application/json" -d '{{"websites":["example.com","google.com"]}}'</code>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 40px; padding: 20px; border-top: 1px solid #e9ecef; color: #6c757d;">
                <p>Made with ❤️ by <a href="https://github.com/fabriziosalmi" target="_blank" style="color: #667eea; text-decoration: none;">Fabrizio Salmi</a> • 
                <a href="https://github.com/fabriziosalmi/websites-monitor" target="_blank" style="color: #667eea; text-decoration: none;">
                    <img src="https://img.shields.io/badge/source-GitHub-181717?logo=github" alt="GitHub" style="vertical-align: middle;">
                </a></p>
            </div>
        </body>
    </html>
    """

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
        version="1.0.0", 
        timestamp=datetime.now(),
        total_checks_available=len(CHECK_FUNCTIONS),
        config_loaded=default_config is not None
    )

@app.get("/checks", tags=["Checks"])
async def list_checks():
    """
    ## List All Available Checks
    
    Returns comprehensive information about all 50+ available website checks, including:
    - Check names and descriptions
    - Categories (security, performance, SEO, etc.)
    - Individual API endpoints
    - Default timeouts and settings
    """
    global default_config
    monitor = WebsiteMonitor(default_config)
    
    checks_info = []
    
    # Add checks from WebsiteMonitor
    for check in monitor.check_functions:
        checks_info.append({
            "name": check.name,
            "slug": check.name.lower().replace(" ", "_").replace("-", "_"),
            "enabled": check.enabled,
            "timeout": check.timeout,
            "description": getattr(check.function, '__doc__', 'No description available').strip() if hasattr(check.function, '__doc__') else "No description available",
            "category": _categorize_check(check.name),
            "endpoint": f"/check/{check.name.lower().replace(' ', '_').replace('-', '_')}"
        })
    
    # Add individual check functions
    for check_name, check_func in CHECK_FUNCTIONS.items():
        # Skip if already in WebsiteMonitor checks
        if not any(c["slug"] == check_name for c in checks_info):
            checks_info.append({
                "name": check_name.replace("_", " ").title(),
                "slug": check_name,
                "enabled": True,
                "timeout": None,
                "description": getattr(check_func, '__doc__', 'No description available').strip() if hasattr(check_func, '__doc__') else "No description available",
                "category": _categorize_check(check_name),
                "endpoint": f"/check/{check_name}"
            })
    
    # Group by category
    categories = {}
    for check in checks_info:
        cat = check["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(check)
    
    return {
        "total_checks": len(checks_info),
        "categories": list(categories.keys()),
        "checks_by_category": categories,
        "all_checks": sorted(checks_info, key=lambda x: x["name"])
    }

def _categorize_check(check_name: str) -> str:
    """Categorize a check based on its name."""
    check_lower = check_name.lower()
    
    if any(word in check_lower for word in ['ssl', 'security', 'hsts', 'xss', 'cors', 'breach', 'blacklist']):
        return "security"
    elif any(word in check_lower for word in ['pagespeed', 'load', 'performance', 'cdn', 'brotli', 'minification']):
        return "performance"  
    elif any(word in check_lower for word in ['seo', 'sitemap', 'robot', 'open_graph', 'alt_tags', 'semantic']):
        return "seo"
    elif any(word in check_lower for word in ['accessibility', 'mobile', 'internationalization', 'i18n']):
        return "accessibility"
    elif any(word in check_lower for word in ['privacy', 'cookie', 'tracking', 'floc', 'whois']):
        return "privacy"
    elif any(word in check_lower for word in ['domain', 'dns', 'subdomain', 'email']):
        return "domain"
    else:
        return "other"

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

@app.get("/monitor/check/{check_name}", tags=["Individual Checks"])
async def run_specific_check(
    check_name: str = Path(..., description="Name of the check to run"),
    website: str = Query(..., description="Website URL or domain to check", example="example.com"),
    timeout: Optional[int] = Query(30, description="Timeout in seconds", ge=5, le=300)
):
    """
    ## Run Individual Check
    
    Execute a specific check on a website. Use the `/checks` endpoint to see all available checks.
    
    **Available Check Categories:**
    - **Security:** ssl_cert, security_headers, xss_protection, cors_headers, etc.
    - **Performance:** pagespeed_performances, website_load_time, cdn, brotli_compression, etc.
    - **SEO:** sitemap, robot_txt, open_graph_protocol, alt_tags, etc.
    - **Privacy:** cookie_policy, privacy_exposure, tracking detection, etc.
    - **Domain:** domain_expiration, dns_blacklist, subdomain_enumeration, etc.
    """
    global default_config
    monitor = WebsiteMonitor(default_config)
    
    # Find the requested check in WebsiteMonitor
    target_check = None
    for check in monitor.check_functions:
        if check.name.lower().replace(" ", "_").replace("-", "_") == check_name.lower():
            target_check = check
            break
    
    # If not found in WebsiteMonitor, try individual check functions
    if not target_check and check_name in CHECK_FUNCTIONS:
        check_func = CHECK_FUNCTIONS[check_name]
        try:
            config = Config(websites=[website], timeout=timeout or 30)
            
            # Handle different function signatures
            if check_name == "pagespeed_performances":
                if asyncio.iscoroutinefunction(check_func):
                    result = await asyncio.wait_for(check_func(f"https://{website}", api_key=config.pagespeed_api_key), timeout)
                else:
                    result = check_func(f"https://{website}", api_key=config.pagespeed_api_key)
            elif check_name == "rate_limiting":
                result = check_func(f"https://{website}")
            elif asyncio.iscoroutinefunction(check_func):
                result = await asyncio.wait_for(check_func(website), timeout)
            else:
                result = check_func(website)
                
            return {
                "check_name": check_name.replace("_", " ").title(),
                "website": website,
                "result": result,
                "timestamp": datetime.now(),
                "status": "completed",
                "execution_time": None
            }
            
        except Exception as e:
            logger.error(f"Individual check {check_name} failed for {website}: {e}")
            raise HTTPException(status_code=500, detail=f"Check failed: {str(e)}")
    
    # If found in WebsiteMonitor, use that
    if target_check:
        try:
            config = Config(websites=[website], timeout=timeout or 30)
            start_time = datetime.now()
            result = await target_check.execute(website, config, config.timeout)
            end_time = datetime.now()
            
            return {
                "check_name": target_check.name,
                "website": website,
                "result": result,
                "timestamp": end_time,
                "status": "completed",
                "execution_time": (end_time - start_time).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"Check {check_name} failed for {website}: {e}")
            raise HTTPException(status_code=500, detail=f"Check failed: {str(e)}")
    
    # Check not found
    available_checks = []
    for check in monitor.check_functions:
        available_checks.append(check.name.lower().replace(" ", "_").replace("-", "_"))
    available_checks.extend(CHECK_FUNCTIONS.keys())
    
    raise HTTPException(
        status_code=404, 
        detail=f"Check '{check_name}' not found. Available checks: {sorted(set(available_checks))}"
    )

# Generate individual endpoints for each check function
def create_check_endpoint(check_name: str, check_func: callable):
    async def endpoint(
        website: str = Query(..., description=f"Website URL or domain to check with {check_name}", example="example.com"),
        timeout: Optional[int] = Query(30, description="Timeout in seconds", ge=5, le=300)
    ):
        try:
            start_time = datetime.now()
            
            # Handle different function signatures  
            if check_name == "pagespeed_performances":
                if asyncio.iscoroutinefunction(check_func):
                    result = await asyncio.wait_for(check_func(f"https://{website}"), timeout)
                else:
                    result = check_func(f"https://{website}")
            elif check_name == "rate_limiting":
                result = check_func(f"https://{website}")
            elif asyncio.iscoroutinefunction(check_func):
                result = await asyncio.wait_for(check_func(website), timeout)
            else:
                result = check_func(website)
            
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
    
    # Get check description
    description = getattr(check_func, '__doc__', f'Run {check_name.replace("_", " ").title()} check').strip()
    endpoint_func.__doc__ = f"""
    ## {check_name.replace('_', ' ').title()} Check
    
    {description}
    
    **Category:** {_categorize_check(check_name).title()}
    **Check Type:** Individual Security/Performance/SEO Analysis
    """
    
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

@app.get("/docs/swagger", response_class=HTMLResponse, tags=["Documentation"])
async def custom_swagger_ui():
    """
    ## Custom Swagger UI
    
    Enhanced Swagger documentation interface with custom styling and additional features.
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Website Monitor API - Swagger UI</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui.css" />
        <style>
            .swagger-ui .topbar { display: none; }
            .swagger-ui .info { margin: 20px 0; }
            .swagger-ui .info .title { color: #667eea; }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-bundle.js"></script>
        <script>
            SwaggerUIBundle({
                url: '/api/openapi.json',
                dom_id: '#swagger-ui',
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.presets.standalone
                ],
                layout: "BaseLayout",
                deepLinking: true,
                showExtensions: true,
                showCommonExtensions: true
            });
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    print("🚀 Starting Website Monitor API...")
    print(f"📊 {len(CHECK_FUNCTIONS)} check functions loaded")
    print("📚 API Documentation will be available at:")
    print("   - http://localhost:8000/api/docs (Swagger UI)")
    print("   - http://localhost:8000/api/redoc (ReDoc)")
    print("   - http://localhost:8000/docs/ (Custom Documentation)")
    print("   - http://localhost:8000/ (API Landing Page)")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
