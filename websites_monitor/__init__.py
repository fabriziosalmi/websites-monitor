"""
Website Monitor: security, performance, SEO, privacy and accessibility
checks for websites.

The package is laid out as ports and adapters:

- domain: verdicts, targets and summaries; pure functions, no I/O.
- ports: what the application needs from the outside (a check runner).
- application: MonitorService, the one implementation of every operation.
- adapters.checks: the check runner backed by the functions in checks/.
- adapters.http, adapters.cli, adapters.mcp: the REST API, the command line
  and the MCP server. Each only translates its own protocol to a
  MonitorService call, so the three return the same JSON for the same
  operation (tests/test_parity.py holds them to it). The web UI calls the
  REST API.
"""

__version__ = "1.5.0"
