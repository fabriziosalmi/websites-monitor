"""
The MCP server: one tool per MonitorService operation, returning the same
JSON as the REST API and the command line.

Run it with: python -m websites_monitor mcp (stdio), or
python -m websites_monitor mcp --transport streamable-http --port 8001.
"""
from __future__ import annotations

import functools
import sys
from typing import Any, Optional

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

from ..application import DEFAULT_CONCURRENCY, DEFAULT_TIMEOUT, OPERATIONS, MonitorService

INSTRUCTIONS = (
    "Website Monitor runs checks against websites: TLS, security headers, "
    "performance, SEO, DNS, privacy and accessibility. Call list_checks to see "
    "the checks, scan to run them against one site, run_check for a single "
    "check. Each result has a verdict (pass, warn, fail, unknown) and a detail; "
    "unknown means the check could not decide, and error or detail says why. "
    "Checks send requests to the site you name, so only scan sites you may test."
)
# Checks change nothing locally, but they send requests to other hosts.
READS_THE_WEB = ToolAnnotations(read_only_hint=True, open_world_hint=True)
LOCAL = ToolAnnotations(read_only_hint=True, open_world_hint=False)


def _explained(tool):
    """
    A bad argument (unknown check, website, format or category) becomes a
    ToolError, whose message reaches the model; any other exception would
    only say "Error executing tool".
    """
    @functools.wraps(tool)
    async def wrapper(*args, **kwargs):
        try:
            result = tool(*args, **kwargs)
            return await result if hasattr(result, "__await__") else result
        except KeyError as e:
            raise ToolError(f"unknown check {e.args[0]!r}: call list_checks for the IDs") from e
        except ValueError as e:
            raise ToolError(str(e)) from e
        finally:
            sys.stdout.flush()  # see run_stdio
    return wrapper


def run_stdio(server: MCPServer) -> None:
    """
    Serve over stdin and stdout. Several checks print(); the SDK points fd 1
    at stderr while it serves, but print() fills Python's stdout buffer, which
    is only flushed at exit, after the SDK has given fd 1 back to the protocol:
    the text then arrived on the wire as a broken JSON-RPC message. Flushing
    at every newline sends it to stderr while the diversion holds.
    """
    sys.stdout.reconfigure(line_buffering=True)
    server.run("stdio")


def create_mcp(service: MonitorService) -> MCPServer:
    server = MCPServer(
        "websites-monitor",
        version=service.health()["version"],
        instructions=INSTRUCTIONS,
    )

    @server.tool(description=OPERATIONS["health"], annotations=LOCAL)
    @_explained
    def health() -> dict[str, Any]:
        return service.health()

    @server.tool(description=OPERATIONS["list_checks"], annotations=LOCAL)
    @_explained
    def list_checks(category: Optional[str] = None) -> dict[str, Any]:
        return service.list_checks(category)

    @server.tool(description=OPERATIONS["run_check"], annotations=READS_THE_WEB)
    @_explained
    async def run_check(check_id: str, website: str, timeout: int = DEFAULT_TIMEOUT,
                        pagespeed_api_key: Optional[str] = None) -> dict[str, Any]:
        return await service.run_check(check_id, website, timeout=timeout, pagespeed_api_key=pagespeed_api_key)

    @server.tool(description=OPERATIONS["scan"], annotations=READS_THE_WEB)
    @_explained
    async def scan(website: str, checks: Optional[list[str]] = None, timeout: int = DEFAULT_TIMEOUT,
                   concurrency: int = DEFAULT_CONCURRENCY, pagespeed_api_key: Optional[str] = None) -> dict[str, Any]:
        return await service.scan(website, checks, timeout=timeout, concurrency=concurrency,
                                  pagespeed_api_key=pagespeed_api_key)

    @server.tool(description=OPERATIONS["scan_many"], annotations=READS_THE_WEB)
    @_explained
    async def scan_many(websites: list[str], timeout: int = DEFAULT_TIMEOUT, concurrency: int = DEFAULT_CONCURRENCY,
                        pagespeed_api_key: Optional[str] = None) -> dict[str, Any]:
        return await service.scan_many(websites, timeout=timeout, concurrency=concurrency,
                                       pagespeed_api_key=pagespeed_api_key)

    @server.tool(description=OPERATIONS["report"], annotations=READS_THE_WEB)
    @_explained
    async def report(websites: list[str], output_format: str = "markdown", timeout: int = DEFAULT_TIMEOUT,
                     concurrency: int = DEFAULT_CONCURRENCY, pagespeed_api_key: Optional[str] = None) -> dict[str, Any]:
        return await service.report(websites, output_format, timeout=timeout, concurrency=concurrency,
                                    pagespeed_api_key=pagespeed_api_key)

    return server
