"""What the application needs from the outside world."""
from __future__ import annotations

from typing import Optional, Protocol

from .domain import CheckSpec


class CheckRunner(Protocol):
    """Runs one check against one website and returns its raw result string."""

    def specs(self) -> list[CheckSpec]:
        """Every check this runner can execute, in catalog order."""

    async def run(self, check_id: str, website: str, *, pagespeed_api_key: Optional[str] = None) -> str:
        """
        The check's result string, such as "🟢 (50 days left)". May raise;
        the application turns an exception or a timeout into no verdict.
        """
