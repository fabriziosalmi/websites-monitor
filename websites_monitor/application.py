"""
MonitorService: the one implementation of every operation.

The REST API, the command line and the MCP server each call these methods
and return their result as is, so an operation gives the same JSON whatever
the interface. OPERATIONS lists them; tests/test_parity.py checks that each
interface exposes all of them and returns the same output.
"""
from __future__ import annotations

import asyncio
import html
import logging
import time
from datetime import datetime, timezone
from typing import Callable, Iterable, Optional

from .domain import CATEGORIES, CheckSpec, normalize_website, parse_result, summarize
from .ports import CheckRunner

logger = logging.getLogger(__name__)

# name -> what it does. The CLI help and the MCP tool descriptions come from here.
OPERATIONS = {
    "health": "Status of the service: version and number of checks.",
    "list_checks": "Every check: ID, name, category and description.",
    "run_check": "Run one check against one website.",
    "scan": "Run the given checks (all of them by default) against one website, with a summary.",
    "scan_many": "Run every check against several websites, grouped by check.",
    "report": "Run every check against several websites and render a report as Markdown, HTML or JSON.",
}
REPORT_FORMATS = ("markdown", "json", "html")
DEFAULT_TIMEOUT = 30
DEFAULT_CONCURRENCY = 4
MAX_CONCURRENCY = 16


def _now() -> datetime:
    return datetime.now(timezone.utc)


class MonitorService:
    def __init__(
        self,
        runner: CheckRunner,
        version: str,
        *,
        config_loaded: bool = True,
        clock: Callable[[], datetime] = _now,
    ):
        self._runner = runner
        self._version = version
        self._config_loaded = config_loaded
        self._clock = clock
        self._specs = {spec.id: spec for spec in runner.specs()}

    # ---------- catalog ----------

    def specs(self) -> list[CheckSpec]:
        return list(self._specs.values())

    def health(self) -> dict:
        return {
            "status": "healthy",
            "version": self._version,
            "timestamp": self._clock().isoformat(),
            "total_checks_available": len(self._specs),
            "config_loaded": self._config_loaded,
        }

    def list_checks(self, category: Optional[str] = None) -> dict:
        if category is not None and category not in CATEGORIES:
            raise ValueError(f"unknown category {category!r}; one of: {', '.join(CATEGORIES)}")
        checks = [
            {
                "slug": spec.id,
                "name": spec.name,
                "category": spec.category,
                "description": spec.description,
                "enabled": True,
                "timeout": spec.min_timeout,
                "endpoint": f"/check/{spec.id}",
            }
            for spec in sorted(self._specs.values(), key=lambda s: s.id)
            if category is None or spec.category == category
        ]
        by_category: dict[str, list] = {}
        for check in checks:
            by_category.setdefault(check["category"], []).append(check)
        return {
            "total_checks": len(checks),
            "categories": list(by_category),
            "checks_by_category": by_category,
            "all_checks": checks,
        }

    # ---------- running checks ----------

    async def run_check(
        self, check_id: str, website: str, *, timeout: int = DEFAULT_TIMEOUT, pagespeed_api_key: Optional[str] = None,
    ) -> dict:
        host = normalize_website(website)
        if check_id not in self._specs:
            raise KeyError(check_id)
        outcome = await self._outcome(check_id, host, timeout, pagespeed_api_key)
        return dict(outcome, execution_time=outcome["duration_ms"] / 1000)

    async def scan(
        self,
        website: str,
        checks: Optional[Iterable[str]] = None,
        *,
        timeout: int = DEFAULT_TIMEOUT,
        concurrency: int = DEFAULT_CONCURRENCY,
        pagespeed_api_key: Optional[str] = None,
    ) -> dict:
        host = normalize_website(website)
        ids = list(dict.fromkeys(checks)) if checks is not None else list(self._specs)
        started = time.monotonic()
        results = await self._gather([(check_id, host) for check_id in ids], timeout, concurrency, pagespeed_api_key)
        return {
            "success": True,
            "message": "Custom monitoring completed successfully",
            "website": host,
            "results": results,
            "summary": summarize(r["verdict"] for r in results),
            "execution_time": time.monotonic() - started,
            "timestamp": self._clock().isoformat(),
            "websites_checked": 1,
            "checks_performed": len(results),
        }

    async def scan_many(
        self,
        websites: Iterable[str],
        *,
        timeout: int = DEFAULT_TIMEOUT,
        concurrency: int = DEFAULT_CONCURRENCY,
        pagespeed_api_key: Optional[str] = None,
    ) -> dict:
        hosts = list(dict.fromkeys(normalize_website(w) for w in websites))
        if not hosts:
            raise ValueError("no website given")
        started = time.monotonic()
        pairs = [(check_id, host) for check_id in self._specs for host in hosts]
        outcomes = await self._gather(pairs, timeout, concurrency, pagespeed_api_key)
        grouped = []
        for spec in self._specs.values():
            per_site = [o for o in outcomes if o["check_id"] == spec.id]
            grouped.append({"check_id": spec.id, "check_name": spec.name, "results": per_site})
        return {
            "success": True,
            "message": "Monitoring completed successfully",
            "results": grouped,
            "summary": summarize(o["verdict"] for o in outcomes),
            "execution_time": time.monotonic() - started,
            "timestamp": self._clock().isoformat(),
            "websites_checked": len(hosts),
            "checks_performed": len(outcomes),
        }

    async def report(
        self,
        websites: Iterable[str],
        output_format: str = "markdown",
        *,
        timeout: int = DEFAULT_TIMEOUT,
        concurrency: int = DEFAULT_CONCURRENCY,
        template: str = "",
        pagespeed_api_key: Optional[str] = None,
    ) -> dict:
        if output_format not in REPORT_FORMATS:
            raise ValueError(f"unknown format {output_format!r}; one of: {', '.join(REPORT_FORMATS)}")
        data = await self.scan_many(websites, timeout=timeout, concurrency=concurrency, pagespeed_api_key=pagespeed_api_key)
        generated = self._clock()
        body: dict = {"format": output_format, "timestamp": generated.isoformat()}
        if output_format == "json":
            body["report_data"] = data
        elif output_format == "markdown":
            body["report_content"] = render_markdown(data, generated, template)
        else:
            body["report_content"] = render_html(data, generated)
        body["websites_count"] = data["websites_checked"]
        body["generation_time"] = generated.isoformat()
        return body

    # ---------- internals ----------

    async def _gather(self, pairs, timeout, concurrency, pagespeed_api_key) -> list[dict]:
        limit = asyncio.Semaphore(max(1, min(MAX_CONCURRENCY, int(concurrency))))

        async def one(check_id, host):
            async with limit:
                return await self._outcome(check_id, host, timeout, pagespeed_api_key)

        return list(await asyncio.gather(*(one(check_id, host) for check_id, host in pairs)))

    async def _outcome(self, check_id: str, host: str, timeout: int, pagespeed_api_key: Optional[str]) -> dict:
        spec = self._specs.get(check_id)
        started = time.monotonic()
        error = None
        if spec is None:
            raw, error = "\u26AA", "Unknown check"
        else:
            limit = spec.timeout_for(timeout)
            try:
                raw = await asyncio.wait_for(
                    self._runner.run(check_id, host, pagespeed_api_key=pagespeed_api_key), timeout=limit,
                )
            except asyncio.TimeoutError:
                logger.warning(f"Check {check_id} timed out for {host}")
                raw, error = "\u26AA", f"Timed out after {limit}s"
            except Exception as e:  # a check must not take the scan down
                logger.error(f"Check {check_id} failed for {host}: {e}")
                raw, error = "\u26AA", str(e) or type(e).__name__
        verdict, detail = parse_result(raw)
        return {
            "check_id": check_id,
            "check_name": spec.name if spec else check_id,
            "category": spec.category if spec else None,
            "website": host,
            "result": str(raw),
            "verdict": verdict,
            "detail": detail,
            "status": "error" if error else "completed",
            "error": error,
            "timestamp": self._clock().isoformat(),
            "duration_ms": round((time.monotonic() - started) * 1000),
        }


# ---------- reports ----------

def _cell(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ").strip()


def render_markdown(data: dict, generated: datetime, template: str = "") -> str:
    """One row per website, one column per check; a cell is the check's result."""
    sites = sorted({o["website"] for group in data["results"] for o in group["results"]})
    head = "# Website Monitor report\n\n"
    if template.strip():
        head += template.strip() + "\n\n"
    head += f"Generated on {generated.strftime('%Y-%m-%d %H:%M:%S UTC')}.\n\n"
    columns = [group["check_name"] for group in data["results"]]
    lines = [
        "| Website | " + " | ".join(_cell(c) for c in columns) + " |",
        "|---------|" + "|".join("---" for _ in columns) + "|",
    ]
    for site in sites:
        cells = []
        for group in data["results"]:
            match = next((o for o in group["results"] if o["website"] == site), None)
            cells.append(_cell(match["result"]) if match else "")
        lines.append(f"| {_cell(site)} | " + " | ".join(cells) + " |")
    return head + "\n".join(lines) + "\n"


def render_html(data: dict, generated: datetime) -> str:
    """The same table as HTML. Every value is escaped: results come from the scanned sites."""
    sites = sorted({o["website"] for group in data["results"] for o in group["results"]})
    rows = []
    for group in data["results"]:
        cells = []
        for site in sites:
            match = next((o for o in group["results"] if o["website"] == site), None)
            verdict = match["verdict"] if match else "unknown"
            cells.append(f'<td class="{verdict}">{html.escape(match["result"]) if match else ""}</td>')
        rows.append(f"<tr><td>{html.escape(group['check_name'])}</td>{''.join(cells)}</tr>")
    header = "".join(f"<th>{html.escape(site)}</th>" for site in sites)
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<title>Website Monitor report</title>\n<style>\n"
        "body { font-family: system-ui, sans-serif; margin: 20px; }\n"
        "table { border-collapse: collapse; width: 100%; }\n"
        "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }\n"
        "th { background: #f2f2f2; }\n"
        ".pass { color: #067647; } .warn { color: #b54708; } .fail { color: #b42318; } .unknown { color: #475467; }\n"
        "</style>\n</head>\n<body>\n<h1>Website Monitor report</h1>\n"
        f"<p>Generated on {generated.strftime('%Y-%m-%d %H:%M:%S UTC')}.</p>\n"
        f"<p>Websites checked: {data['websites_checked']}. Execution time: {data['execution_time']:.2f} s.</p>\n"
        f"<table>\n<thead><tr><th>Check</th>{header}</tr></thead>\n<tbody>\n"
        + "\n".join(rows)
        + "\n</tbody>\n</table>\n</body>\n</html>\n"
    )
