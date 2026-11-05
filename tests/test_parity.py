"""
The REST API, the command line and the MCP server expose the same operations
and return the same JSON for the same input. The web UI calls the REST API.
"""
import asyncio
import io
import json
import pathlib
import re
from contextlib import redirect_stdout

import pytest
from fastapi.testclient import TestClient

from fakes import make_service
from websites_monitor.adapters.cli import COMMANDS, build_parser, main as cli_main
from websites_monitor.adapters.http import create_app
from websites_monitor.adapters.mcp import create_mcp
from websites_monitor.application import OPERATIONS

VOLATILE = {"timestamp", "execution_time", "duration_ms", "generation_time"}
APP_JS = (pathlib.Path(__file__).resolve().parent.parent / "docs" / "assets" / "app.js").read_text(encoding="utf-8")

# operation -> (HTTP call, CLI argv, MCP arguments), all with the same input.
CASES = {
    "health": (("get", "/health", None), ["health"], {}),
    "list_checks": (("get", "/checks?category=security", None), ["checks", "--category", "security"], {"category": "security"}),
    "run_check": (("get", "/check/ssl_cert?website=https://example.com/", None),
                  ["check", "ssl_cert", "https://example.com/"], {"check_id": "ssl_cert", "website": "https://example.com/"}),
    "scan": (("post", "/monitor/single", {"website": "example.com", "checks": ["hsts", "cdn", "nope"], "timeout": 5}),
             ["scan", "example.com", "--checks", "hsts,cdn,nope", "--timeout", "5"],
             {"website": "example.com", "checks": ["hsts", "cdn", "nope"], "timeout": 5}),
    "scan_many": (("post", "/monitor", {"websites": ["a.test", "b.test"], "timeout": 5}),
                  ["scan-many", "a.test", "b.test", "--timeout", "5"], {"websites": ["a.test", "b.test"], "timeout": 5}),
    "report": (("post", "/generate-report", {"websites": ["a.test"], "output_format": "json", "timeout": 5}),
               ["report", "a.test", "--format", "json", "--timeout", "5", "--config", "/nonexistent.yaml"],
               {"websites": ["a.test"], "output_format": "json", "timeout": 5}),
}


def stable(value):
    """The output without the fields that differ between two runs."""
    if isinstance(value, dict):
        return {k: stable(v) for k, v in value.items() if k not in VOLATILE}
    if isinstance(value, list):
        return [stable(v) for v in value]
    return value


def via_http(case):
    method, path, body = case
    service, _ = make_service(slow_seconds=0)
    response = getattr(TestClient(create_app(service)), method)(path, **({"json": body} if body else {}))
    assert response.status_code == 200, response.text
    return response.json()


def via_cli(argv):
    service, _ = make_service(slow_seconds=0)
    out = io.StringIO()
    with redirect_stdout(out):
        assert cli_main([*argv, "--json"], service=service) == 0
    return json.loads(out.getvalue())


def via_mcp(name, arguments):
    service, _ = make_service(slow_seconds=0)
    result = asyncio.run(create_mcp(service).call_tool(name, arguments))
    assert not result.is_error
    return result.structured_content


def test_every_operation_has_a_case():
    assert set(CASES) == set(OPERATIONS)


def test_every_interface_exposes_every_operation():
    commands = set(build_parser()._subparsers._group_actions[0].choices)
    assert {COMMANDS[op] for op in OPERATIONS} <= commands
    tools = {t.name for t in asyncio.run(create_mcp(make_service()[0]).list_tools())}
    assert tools == set(OPERATIONS)
    service, _ = make_service()
    summaries = {route.summary for route in create_app(service).routes if getattr(route, "summary", None)}
    assert {op for op in OPERATIONS} <= {s.split(" ")[0] for s in summaries}


@pytest.mark.parametrize("operation", sorted(CASES))
def test_the_three_interfaces_return_the_same_json(operation):
    http_case, argv, arguments = CASES[operation]

    from_http = stable(via_http(http_case))
    from_cli = stable(via_cli(argv))
    from_mcp = stable(via_mcp(operation, arguments))

    assert from_cli == from_http
    assert from_mcp == from_http


def test_the_web_ui_calls_the_rest_api_for_its_operations():
    # health (sidebar), list_checks (catalog), scan and run_check (a scan of
    # one check, used by Retry) go through these endpoints.
    for path in ("/health", "/checks", "/monitor/single"):
        assert re.search(rf"fetchJson\('{re.escape(path)}'", APP_JS), path


def _object_keys(source, start_marker):
    block = source[source.index(start_marker):]
    block = block[block.index("{"):]
    depth, end = 0, 0
    for i, ch in enumerate(block):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    body = block[:end]
    # top-level keys only: drop nested braces
    flat, depth = [], 0
    for ch in body[1:]:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        elif depth == 0:
            flat.append(ch)
    keys = set()
    for segment in "".join(flat).split(","):
        segment = segment.strip()
        if segment:
            keys.add(segment.split(":")[0].strip())  # "key: value" or shorthand "key"
    return keys


def test_the_web_ui_exports_the_same_json_as_the_scan_operation():
    from websites_monitor.adapters.http import Outcome, ScanResponse

    export = APP_JS[APP_JS.index("function exportJson(entry)"):]
    doc_keys = _object_keys(export, "const doc = {")
    outcome_keys = _object_keys(export, "r.outcome ? r.outcome : {")

    assert doc_keys == set(ScanResponse.model_fields)
    assert outcome_keys == set(Outcome.model_fields)
