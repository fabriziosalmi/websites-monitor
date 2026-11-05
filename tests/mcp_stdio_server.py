"""Started as a subprocess by test_mcp_stdio.py: an MCP server whose check prints."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from fakes import FakeRunner  # noqa: E402
from websites_monitor.adapters.mcp import create_mcp, run_stdio  # noqa: E402
from websites_monitor.application import MonitorService  # noqa: E402


class PrintingRunner(FakeRunner):
    async def run(self, check_id, website, *, pagespeed_api_key=None):
        print(f"a check printed this for {website}")  # what several real checks do
        return await super().run(check_id, website, pagespeed_api_key=pagespeed_api_key)


run_stdio(create_mcp(MonitorService(PrintingRunner(slow_seconds=0), "9.9.9")))
