"""The MCP server: one tool per operation, described for a model to use."""
import asyncio

import pytest
from mcp.server.mcpserver.exceptions import ToolError

from fakes import make_service
from websites_monitor.adapters.mcp import create_mcp
from websites_monitor.application import OPERATIONS


def server():
    service, _ = make_service(slow_seconds=0)
    return create_mcp(service)


def test_there_is_one_tool_per_operation_with_its_description():
    tools = {t.name: t for t in asyncio.run(server().list_tools())}

    assert set(tools) == set(OPERATIONS)
    for name, tool in tools.items():
        assert tool.description == OPERATIONS[name]


def test_tools_say_whether_they_reach_the_network():
    tools = {t.name: t for t in asyncio.run(server().list_tools())}

    for name in ("run_check", "scan", "scan_many", "report"):
        assert tools[name].annotations.read_only_hint and tools[name].annotations.open_world_hint, name
    for name in ("health", "list_checks"):
        assert tools[name].annotations.read_only_hint and not tools[name].annotations.open_world_hint, name


def test_a_tool_returns_structured_json():
    result = asyncio.run(server().call_tool("scan", {"website": "example.com", "checks": ["ssl_cert"]}))

    assert not result.is_error
    assert result.structured_content["results"][0]["verdict"] == "pass"


def test_bad_arguments_are_a_tool_error():
    with pytest.raises(ToolError):
        asyncio.run(server().call_tool("scan", {"website": 3}))


@pytest.mark.parametrize("tool, arguments, message", [
    ("run_check", {"check_id": "nope", "website": "example.com"}, "unknown check 'nope'"),
    ("scan", {"website": "   "}, "website is empty"),
    ("report", {"websites": ["example.com"], "output_format": "pdf"}, "unknown format 'pdf'"),
    ("list_checks", {"category": "nope"}, "unknown category 'nope'"),
])
def test_a_bad_argument_explains_itself(tool, arguments, message):
    with pytest.raises(ToolError) as error:
        asyncio.run(server().call_tool(tool, arguments))
    assert message in str(error.value)
