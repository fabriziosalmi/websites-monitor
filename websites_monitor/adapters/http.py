"""
The REST API. Each route translates HTTP to one MonitorService call and
returns its result as is; the CLI and the MCP server return the same JSON.
"""
from __future__ import annotations

import logging
import threading
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException, Path as PathParam, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from ..application import DEFAULT_CONCURRENCY, DEFAULT_TIMEOUT, MAX_CONCURRENCY, MonitorService
from ..domain import normalize_website

logger = logging.getLogger(__name__)

DOCS_DIR = Path(__file__).resolve().parents[2] / "docs"
SWAGGER_VERSION = "5.34.0"
REDOC_VERSION = "2.5.4"
# The ReDoc page loads only what this server serves. The one outside request in
# the bundle, the Redocly logo in the footer, is blocked and hides itself.
REDOC_CSP = (
    "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; connect-src 'self'; worker-src blob:; font-src 'self' data:"
)

TimeoutField = Field(DEFAULT_TIMEOUT, description="Seconds each check may take", ge=5, le=300)
ConcurrencyField = Field(DEFAULT_CONCURRENCY, description="Checks run at the same time", ge=1, le=MAX_CONCURRENCY)
KeyField = Field(None, description="Google PageSpeed Insights API key for this request; defaults to PAGESPEED_API_KEY")


# ---------- requests ----------

class ScanRequest(BaseModel):
    website: str = Field(..., description="Domain or URL; only the host is used", examples=["example.com"])
    checks: Optional[List[str]] = Field(None, description="Check IDs to run, in order; all of them when omitted", examples=[["ssl_cert", "hsts"]])
    timeout: Optional[int] = TimeoutField
    concurrency: Optional[int] = ConcurrencyField
    pagespeed_api_key: Optional[str] = KeyField

    @field_validator("website")
    @classmethod
    def host_only(cls, value: str) -> str:
        return normalize_website(value)


class ScanManyRequest(BaseModel):
    websites: List[str] = Field(..., description="Domains or URLs; only the hosts are used", examples=[["example.com", "example.org"]])
    timeout: Optional[int] = TimeoutField
    concurrency: Optional[int] = ConcurrencyField
    pagespeed_api_key: Optional[str] = KeyField

    @field_validator("websites")
    @classmethod
    def hosts_only(cls, values: List[str]) -> List[str]:
        return [normalize_website(v) for v in values]


class ReportRequest(ScanManyRequest):
    output_format: str = Field("markdown", description="markdown, json or html", pattern="^(markdown|json|html)$")
    include_timestamp: bool = Field(True, description="Kept for compatibility; the report always carries its date")


# ---------- responses ----------

class Outcome(BaseModel):
    check_id: str
    check_name: str
    category: Optional[str]
    website: str
    result: str = Field(..., description="The check's result string: a verdict symbol, then an optional detail in parentheses")
    verdict: str = Field(..., description="pass, warn, fail or unknown (no verdict)")
    detail: str
    status: str = Field(..., description="completed, or error when the check raised or timed out")
    error: Optional[str]
    timestamp: str
    duration_ms: int


class CheckRun(Outcome):
    execution_time: float


class Summary(BaseModel):
    total: int
    passed: int
    warnings: int
    failed: int
    no_verdict: int
    pass_rate_percent: Optional[int]


class ScanResponse(BaseModel):
    success: bool
    message: str
    website: str
    results: List[Outcome]
    summary: Summary
    execution_time: float
    timestamp: str
    websites_checked: int
    checks_performed: int


class CheckGroup(BaseModel):
    check_id: str
    check_name: str
    results: List[Outcome]


class ScanManyResponse(BaseModel):
    success: bool
    message: str
    results: List[CheckGroup]
    summary: Summary
    execution_time: float
    timestamp: str
    websites_checked: int
    checks_performed: int


class Health(BaseModel):
    status: str
    version: str
    timestamp: str
    total_checks_available: int
    config_loaded: bool


def create_app(service: MonitorService, *, on_startup: Optional[Callable[[], None]] = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if on_startup is not None:
            threading.Thread(target=on_startup, daemon=True).start()
        yield

    app = FastAPI(
        title="Website Monitor API",
        description=(
            "Runs security, performance, SEO, privacy and accessibility checks "
            "against a website. Each check returns a verdict: pass, warning, fail, "
            "or no verdict when it could not run. GET /checks lists them; "
            "POST /monitor/single runs a selection against one site, and "
            "GET /check/{name} runs a single check. The command line "
            "(python -m websites_monitor) and the MCP server return the same JSON."
        ),
        version=service.health()["version"],
        docs_url=None,
        redoc_url=None,
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    if DOCS_DIR.is_dir():
        app.mount("/docs", StaticFiles(directory=str(DOCS_DIR), html=True), name="docs")
    tasks: Dict[str, Dict[str, Any]] = {}

    def bad_request(e: Exception) -> HTTPException:
        return HTTPException(status_code=422, detail=str(e))

    @app.get("/", include_in_schema=False)
    async def root():
        """The web UI lives under /docs/, where its assets are served."""
        if not (DOCS_DIR / "index.html").exists():
            raise HTTPException(status_code=404, detail="Frontend interface not found")
        return RedirectResponse(url="/docs/", status_code=307)

    @app.get("/api/docs", include_in_schema=False)
    async def swagger_ui():
        """Swagger UI from the vendored copy: the default page loads it from a CDN."""
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - Swagger UI",
            swagger_js_url=f"/docs/vendor/swagger-ui-bundle.js?v={SWAGGER_VERSION}",
            swagger_css_url=f"/docs/vendor/swagger-ui-dist/swagger-ui.css?v={SWAGGER_VERSION}",
            swagger_favicon_url="/docs/favicon.svg?v=2",
        )

    @app.get("/api/redoc", include_in_schema=False)
    async def redoc():
        """ReDoc from the vendored copy, without Google Fonts: the default page loads both from outside."""
        page = get_redoc_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - ReDoc",
            redoc_js_url=f"/docs/vendor/redoc/redoc.standalone.js?v={REDOC_VERSION}",
            redoc_favicon_url="/docs/favicon.svg?v=2",
            with_google_fonts=False,
        )
        page.headers["Content-Security-Policy"] = REDOC_CSP
        return page

    @app.get("/api", include_in_schema=False)
    async def api_landing():
        return RedirectResponse(url="/api/docs", status_code=307)

    @app.get("/health", response_model=Health, tags=["Health"], summary="health")
    async def health():
        return service.health()

    @app.get("/checks", tags=["Checks"], summary="list_checks")
    async def list_checks(category: Optional[str] = Query(None, description="Only the checks of this category")):
        """Every check: ID (slug), name, category, description and its own endpoint."""
        try:
            return service.list_checks(category)
        except ValueError as e:
            raise bad_request(e)

    @app.post("/monitor/single", response_model=ScanResponse, tags=["Monitoring"], summary="scan")
    async def scan(request: ScanRequest):
        """Run the given checks (all of them when checks is omitted) against one website."""
        return await service.scan(
            request.website, request.checks, timeout=request.timeout or DEFAULT_TIMEOUT,
            concurrency=request.concurrency or DEFAULT_CONCURRENCY, pagespeed_api_key=request.pagespeed_api_key,
        )

    @app.get("/monitor/single", response_model=ScanResponse, tags=["Monitoring"], summary="scan (all checks)")
    async def scan_all(
        website: str = Query(..., description="Domain or URL", examples=["example.com"]),
        timeout: Optional[int] = Query(DEFAULT_TIMEOUT, ge=5, le=300),
        pagespeed_api_key: Optional[str] = Query(None),
    ):
        """Run every check against one website: the same response as POST /monitor/single."""
        try:
            host = normalize_website(website)
        except ValueError as e:
            raise bad_request(e)
        return await service.scan(host, None, timeout=timeout or DEFAULT_TIMEOUT, pagespeed_api_key=pagespeed_api_key)

    @app.post("/monitor", response_model=ScanManyResponse, tags=["Monitoring"], summary="scan_many")
    async def scan_many(request: ScanManyRequest):
        """Run every check against several websites; results are grouped by check."""
        try:
            return await service.scan_many(
                request.websites, timeout=request.timeout or DEFAULT_TIMEOUT,
                concurrency=request.concurrency or DEFAULT_CONCURRENCY, pagespeed_api_key=request.pagespeed_api_key,
            )
        except ValueError as e:
            raise bad_request(e)

    @app.post("/generate-report", tags=["Reports"], summary="report")
    async def report(request: ReportRequest):
        """Run every check against several websites and render the result as Markdown, HTML or JSON."""
        try:
            return await service.report(
                request.websites, request.output_format, timeout=request.timeout or DEFAULT_TIMEOUT,
                concurrency=request.concurrency or DEFAULT_CONCURRENCY, pagespeed_api_key=request.pagespeed_api_key,
            )
        except ValueError as e:
            raise bad_request(e)

    @app.post("/monitor/async", tags=["Async Monitoring"])
    async def scan_many_async(request: ScanManyRequest, background_tasks: BackgroundTasks):
        """Start scan_many in the background and return a task ID to poll (HTTP only)."""
        task_id = str(uuid.uuid4())
        tasks[task_id] = {"status": "running", "started_at": datetime.now(timezone.utc).isoformat(), "websites": request.websites}

        async def run():
            try:
                result = await service.scan_many(
                    request.websites, timeout=request.timeout or DEFAULT_TIMEOUT,
                    concurrency=request.concurrency or DEFAULT_CONCURRENCY, pagespeed_api_key=request.pagespeed_api_key,
                )
                tasks[task_id].update(status="completed", completed_at=datetime.now(timezone.utc).isoformat(), result=result)
            except Exception as e:
                tasks[task_id].update(status="failed", failed_at=datetime.now(timezone.utc).isoformat(), error=str(e))

        background_tasks.add_task(run)
        return {"task_id": task_id, "status": "started", "check_status_url": f"/monitor/async/{task_id}"}

    @app.get("/monitor/async/{task_id}", tags=["Async Monitoring"])
    async def scan_many_async_status(task_id: str = PathParam(..., description="ID returned by POST /monitor/async")):
        """running, completed (with result) or failed (with error). Tasks live in memory."""
        if task_id not in tasks:
            raise HTTPException(status_code=404, detail="Task not found")
        return tasks[task_id]

    for spec in service.specs():
        _add_check_route(app, service, spec)

    return app


def _add_check_route(app: FastAPI, service: MonitorService, spec) -> None:
    async def endpoint(
        website: str = Query(..., description="Domain or URL", examples=["example.com"]),
        timeout: Optional[int] = Query(DEFAULT_TIMEOUT, ge=5, le=300),
        pagespeed_api_key: Optional[str] = Query(None),
    ):
        try:
            return await service.run_check(spec.id, website, timeout=timeout or DEFAULT_TIMEOUT, pagespeed_api_key=pagespeed_api_key)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

    endpoint.__name__ = f"check_{spec.id}"
    endpoint.__doc__ = f"## {spec.name}\n\n{spec.description}\n\n**Category:** {spec.category}"
    app.get(f"/check/{spec.id}", response_model=CheckRun, tags=["Individual Checks"], summary=f"run_check {spec.id}")(endpoint)
