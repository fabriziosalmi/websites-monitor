"""Started as a subprocess by test_mcp_stdio.py: the SDK client, over stdio."""
import asyncio
import pathlib
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = pathlib.Path(__file__).resolve().parent / "mcp_stdio_server.py"


async def main():
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER)])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("scan", {"website": "example.com", "checks": ["ssl_cert", "hsts"]})
            print("verdicts:", [r["verdict"] for r in result.structured_content["results"]])


asyncio.run(main())
