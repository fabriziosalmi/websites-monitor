"""
The command line: python -m websites_monitor <command>.

Every command is one MonitorService operation. With --json it prints the
same JSON the REST API returns for that operation; without, a short text
for people. Exit codes: 0 done, 1 a --fail-on threshold was reached,
2 bad usage, 3 the operation failed (bad website, unknown check or format).
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from typing import Optional, Sequence

from ..application import DEFAULT_CONCURRENCY, DEFAULT_TIMEOUT, OPERATIONS, REPORT_FORMATS, MonitorService
from ..bootstrap import build_service, load_config, read_template
from ..domain import CATEGORIES

SYMBOLS = {"pass": "PASS", "warn": "WARN", "fail": "FAIL", "unknown": "----"}
# operation -> command name
COMMANDS = {
    "health": "health",
    "list_checks": "checks",
    "run_check": "check",
    "scan": "scan",
    "scan_many": "scan-many",
    "report": "report",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="websites-monitor",
        description="Security, performance, SEO, privacy and accessibility checks for websites.",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="log what the checks do (on stderr)")
    sub = parser.add_subparsers(dest="command", required=True, metavar="command")

    def add(operation: str, **kwargs) -> argparse.ArgumentParser:
        p = sub.add_parser(COMMANDS[operation], help=OPERATIONS[operation], description=OPERATIONS[operation], **kwargs)
        p.add_argument("--json", action="store_true", help="print the JSON the REST API returns")
        return p

    def run_options(p: argparse.ArgumentParser, concurrency: bool = True) -> None:
        p.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="seconds each check may take (default %(default)s)")
        if concurrency:
            p.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY, help="checks at the same time (default %(default)s)")
        p.add_argument("--pagespeed-api-key", default=None, help="defaults to PAGESPEED_API_KEY")

    def fail_on(p: argparse.ArgumentParser) -> None:
        p.add_argument("--fail-on", choices=("never", "fail", "warn"), default="never",
                       help="exit 1 if a check failed (fail) or failed or warned (warn); default never")

    add("health")
    p = add("list_checks")
    p.add_argument("--category", choices=CATEGORIES, help="only this category")
    p = add("run_check")
    p.add_argument("check_id", help="a check ID, see the checks command")
    p.add_argument("website", help="domain or URL")
    run_options(p, concurrency=False)
    fail_on(p)
    p = add("scan")
    p.add_argument("website", help="domain or URL")
    p.add_argument("--checks", help="comma-separated check IDs (default: all)")
    run_options(p)
    fail_on(p)
    p = add("scan_many")
    p.add_argument("websites", nargs="+", help="domains or URLs")
    run_options(p)
    fail_on(p)
    p = add("report")
    p.add_argument("websites", nargs="*", help="domains or URLs (default: the websites in config.yaml)")
    p.add_argument("--format", choices=REPORT_FORMATS, default="markdown", dest="output_format")
    p.add_argument("--output", help="write the report here instead of printing it")
    p.add_argument("--config", default="config.yaml", help="config file for the default websites and template")
    run_options(p)

    p = sub.add_parser("serve", help="Run the REST API and the web UI.", description="Run the REST API and the web UI.")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    p = sub.add_parser("mcp", help="Run the MCP server.", description="Run the MCP server for AI assistants.")
    p.add_argument("--transport", choices=("stdio", "streamable-http"), default="stdio")
    p.add_argument("--host", default="127.0.0.1", help="streamable-http only")
    p.add_argument("--port", type=int, default=8001, help="streamable-http only")
    return parser


def _verdicts(result: dict, command: str) -> list[str]:
    if command == "check":
        return [result["verdict"]]
    if command == "scan":
        return [r["verdict"] for r in result["results"]]
    if command == "scan-many":
        return [o["verdict"] for g in result["results"] for o in g["results"]]
    return []


def _text(result: dict, command: str) -> str:
    if command == "health":
        return f"{result['status']}, version {result['version']}, {result['total_checks_available']} checks"
    if command == "checks":
        return "\n".join(f"{c['slug']:<30} {c['category']:<14} {c['name']}" for c in result["all_checks"])
    if command == "check":
        return _line(result)
    if command == "scan":
        s = result["summary"]
        lines = [_line(r) for r in result["results"]]
        lines.append(f"\n{result['website']}: {s['passed']} passed, {s['warnings']} warnings, "
                     f"{s['failed']} failed, {s['no_verdict']} no verdict ({result['execution_time']:.1f} s)")
        return "\n".join(lines)
    if command == "scan-many":
        lines = [_line(o) for g in result["results"] for o in g["results"]]
        s = result["summary"]
        lines.append(f"\n{result['websites_checked']} websites: {s['passed']} passed, {s['warnings']} warnings, "
                     f"{s['failed']} failed, {s['no_verdict']} no verdict ({result['execution_time']:.1f} s)")
        return "\n".join(lines)
    if command == "report":
        return result["report_content"] if "report_content" in result else json.dumps(result["report_data"], indent=2)
    return json.dumps(result, indent=2)


def _line(outcome: dict) -> str:
    note = outcome["error"] or outcome["detail"]
    return f"{SYMBOLS.get(outcome['verdict'], '----')}  {outcome['website']:<24} {outcome['check_id']:<28} {note}".rstrip()


async def run(args: argparse.Namespace, service: MonitorService) -> dict:
    if args.command == "health":
        return service.health()
    if args.command == "checks":
        return service.list_checks(args.category)
    if args.command == "check":
        return await service.run_check(args.check_id, args.website, timeout=args.timeout, pagespeed_api_key=args.pagespeed_api_key)
    if args.command == "scan":
        checks = [c.strip() for c in args.checks.split(",") if c.strip()] if args.checks else None
        return await service.scan(args.website, checks, timeout=args.timeout, concurrency=args.concurrency,
                                  pagespeed_api_key=args.pagespeed_api_key)
    if args.command == "scan-many":
        return await service.scan_many(args.websites, timeout=args.timeout, concurrency=args.concurrency,
                                       pagespeed_api_key=args.pagespeed_api_key)
    if args.command == "report":
        config = load_config(args.config)
        return await service.report(args.websites or config.websites, args.output_format, timeout=args.timeout,
                                    concurrency=args.concurrency, template=read_template(config.report_template),
                                    pagespeed_api_key=args.pagespeed_api_key)
    raise ValueError(f"unknown command {args.command}")


def _log_level(args: argparse.Namespace) -> None:
    """
    22 checks call logging.basicConfig(level=INFO) when imported, which
    happens while the service is built: the level is set after that, or a
    scan would bury its result under their log lines.
    """
    verbose = args.verbose or args.command == "serve"
    logging.getLogger().setLevel(logging.INFO if verbose else logging.WARNING)


def main(argv: Optional[Sequence[str]] = None, service: Optional[MonitorService] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "serve":
        import uvicorn
        from .http import create_app
        from checks.check_domainsblacklists_blacklist import prefetch_blacklist
        app = create_app(service or build_service(), on_startup=prefetch_blacklist)
        _log_level(args)
        uvicorn.run(app, host=args.host, port=args.port)
        return 0
    if args.command == "mcp":
        from .mcp import create_mcp, run_stdio
        server = create_mcp(service or build_service())
        _log_level(args)
        if args.transport == "stdio":
            run_stdio(server)
        else:
            server.run("streamable-http", host=args.host, port=args.port)
        return 0

    service = service or build_service()
    _log_level(args)
    try:
        result = asyncio.run(run(args, service))
    except KeyError as e:
        print(f"error: unknown check {e.args[0]!r}; list them with: websites-monitor checks", file=sys.stderr)
        return 3
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 3

    output = json.dumps(result, indent=2, ensure_ascii=False) if args.json else _text(result, args.command)
    if args.command == "report" and args.output:
        with open(args.output, "w") as f:
            f.write(result.get("report_content") or json.dumps(result.get("report_data"), indent=2, ensure_ascii=False))
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(output)

    threshold = getattr(args, "fail_on", "never")
    verdicts = _verdicts(result, args.command)
    if threshold == "fail" and "fail" in verdicts:
        return 1
    if threshold == "warn" and ("fail" in verdicts or "warn" in verdicts):
        return 1
    return 0
