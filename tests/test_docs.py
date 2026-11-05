"""
The README documents what the code has, and only that: every endpoint, CLI
command, MCP tool and environment variable, and nothing that does not exist.
"""
import asyncio
import json
import re
from pathlib import Path

from fakes import make_service
from websites_monitor.adapters.cli import build_parser
from websites_monitor.adapters.mcp import create_mcp

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text()
# Other pages that cite endpoints and commands; they must not cite what does not exist.
OTHER_DOCS = [ROOT / "docs" / "llms.txt", ROOT / "docs" / "DOCKER.md", ROOT / "CONTRIBUTING.md"]


def endpoints() -> set[str]:
    """METHOD /path from the OpenAPI snapshot; the per-check routes count as /check/{id}."""
    paths = json.loads((ROOT / "docs" / "openapi.json").read_text())["paths"]
    found = set()
    for path, methods in paths.items():
        if path.startswith("/check/") and "{" not in path:
            path = "/check/{id}"
        found |= {f"{method.upper()} {path}" for method in methods}
    return found


def cited_endpoints(text: str) -> set[str]:
    return {m.group(1) for m in re.finditer(r"`((?:GET|POST|PUT|PATCH|DELETE) /[^`?\s]*)", text)}


def commands() -> set[str]:
    sub = next(a for a in build_parser()._actions if a.__class__.__name__ == "_SubParsersAction")
    return set(sub.choices)


def cited_commands(text: str) -> set[str]:
    shell = re.findall(r"(?:\bwebsites-monitor|python -m websites_monitor) ([a-z][a-z-]*)", text)
    json_args = re.findall(r'"websites-monitor", "([a-z][a-z-]*)"', text)
    return set(shell) | set(json_args)


def tools() -> set[str]:
    service, _ = make_service(slow_seconds=0)
    return {t.name for t in asyncio.run(create_mcp(service).list_tools())}


def variables() -> set[str]:
    """Every variable the code, the Compose file or .env.example reads."""
    found = set()
    sources = [ROOT / "api.py", ROOT / "main.py",
               *(ROOT / "websites_monitor").rglob("*.py"), *(ROOT / "checks").glob("*.py")]
    for path in sources:
        found |= set(re.findall(r"""(?:environ(?:\.get)?[\[(]|getenv\()["']([A-Z][A-Z0-9_]+)["']""", path.read_text()))
    found |= set(re.findall(r"\$\{([A-Z][A-Z0-9_]+)", (ROOT / "docker-compose.yml").read_text()))
    found |= set(re.findall(r"^([A-Z][A-Z0-9_]+)=", (ROOT / ".env.example").read_text(), re.M))
    return found


def section(title: str) -> str:
    match = re.search(rf"^## {re.escape(title)}\n(.*?)(?=^## )", README, re.S | re.M)
    assert match, f"README has no '## {title}' section"
    return match.group(1)


def test_the_readme_cites_every_endpoint_and_no_other():
    assert endpoints() == cited_endpoints(section("REST API"))
    for path in OTHER_DOCS:
        assert cited_endpoints(path.read_text()) <= endpoints(), path.name


def test_the_readme_cites_every_command_and_no_other():
    assert cited_commands(README) == commands()
    for path in OTHER_DOCS:
        assert cited_commands(path.read_text()) <= commands(), path.name


def test_the_interfaces_table_lists_every_operation_once_per_interface():
    rows = [line.split("|")[1:-1] for line in section("Interfaces").splitlines()
            if line.startswith("| ") and "`" in line]
    operations = {cells[0].strip() for cells in rows}
    assert operations == tools()
    for cells in rows:
        operation, rest, cli, mcp_tool = (c.strip() for c in cells[:4])
        assert cited_endpoints(rest) <= endpoints(), operation
        assert cited_commands(cli) <= commands(), operation
        assert mcp_tool == f"`{operation}`"


def test_the_readme_lists_every_mcp_tool_and_no_other():
    listed = re.search(r"one tool per operation \(([^)]*)\)", section("MCP server"))
    assert listed, "the MCP server section no longer lists its tools"
    assert set(re.findall(r"`([a-z_]+)`", listed.group(1))) == tools()


def test_the_environment_table_lists_every_variable_and_no_other():
    table = section("Configuration").split("Environment variables", 1)[1]
    documented = {v for line in table.splitlines() if line.startswith("| `")
                  for v in re.findall(r"`([A-Z][A-Z0-9_]+)`", line.split("|")[1])}
    assert documented == variables()
