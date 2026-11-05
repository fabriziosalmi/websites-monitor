"""A check runner with canned results: the application without the network."""
import asyncio
from datetime import datetime, timezone

from websites_monitor.application import MonitorService
from websites_monitor.domain import CheckSpec

SPECS = [
    CheckSpec("ssl_cert", "SSL certificate", "security", "Validity of the certificate."),
    CheckSpec("hsts", "HSTS", "security", "Strict-Transport-Security header."),
    CheckSpec("cdn", "CDN", "performance", "Content delivery network."),
    CheckSpec("slow", "Slow check", "technical", "Takes too long.", min_timeout=None),
    CheckSpec("broken", "Broken check", "technical", "Raises."),
]
RESULTS = {
    "ssl_cert": "\U0001F7E2 (50 days left)",
    "hsts": "\U0001F534",
    "cdn": "\U0001F7E1",
}
FIXED_NOW = datetime(2026, 11, 5, 12, 0, 0, tzinfo=timezone.utc)


class FakeRunner:
    def __init__(self, specs=None, results=None, slow_seconds=10):
        self._specs = specs if specs is not None else SPECS
        self._results = results if results is not None else RESULTS
        self.slow_seconds = slow_seconds
        self.calls = []
        self.in_flight = 0
        self.max_in_flight = 0

    def specs(self):
        return list(self._specs)

    async def run(self, check_id, website, *, pagespeed_api_key=None):
        self.calls.append((check_id, website, pagespeed_api_key))
        self.in_flight += 1
        self.max_in_flight = max(self.max_in_flight, self.in_flight)
        try:
            await asyncio.sleep(0.01)
            if check_id == "slow":
                await asyncio.sleep(self.slow_seconds)
            if check_id == "broken":
                raise ValueError("boom")
            return self._results[check_id]
        finally:
            self.in_flight -= 1


def make_service(**runner_kwargs):
    runner = FakeRunner(**runner_kwargs)
    return MonitorService(runner, "9.9.9", clock=lambda: FIXED_NOW), runner
