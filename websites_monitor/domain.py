"""Verdicts, targets and summaries. Pure functions: no I/O, no clock."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional
from urllib.parse import urlsplit

# A check returns a string that starts with one of these symbols, optionally
# followed by a detail in parentheses: "🟢 (50 days left)".
VERDICT_SYMBOLS = (
    ("\U0001F7E2", "pass"),
    ("\U0001F7E1", "warn"),
    ("\U0001F7E0", "warn"),
    ("\U0001F534", "fail"),
    ("⚪", "unknown"),
)
VERDICTS = ("pass", "warn", "fail", "unknown")
CATEGORIES = ("security", "performance", "seo", "domain", "privacy", "accessibility", "technical")
NO_VERDICT_SYMBOL = "⚪"


@dataclass(frozen=True)
class CheckSpec:
    """A check the runner can execute."""

    id: str
    name: str
    category: str
    description: str
    min_timeout: Optional[int] = None

    def timeout_for(self, requested: int) -> int:
        """Some checks need longer than the default (PageSpeed, DNS blocklists)."""
        return max(requested, self.min_timeout or 0)


def parse_result(raw: object) -> tuple[str, str]:
    """
    The verdict and the detail of a check's result string.

    The verdict is the first verdict symbol in the string; the detail is the
    rest, without the surrounding parentheses. A string without a symbol is
    no verdict, with the whole string as detail.
    """
    text = "" if raw is None else str(raw).strip()
    verdict = "unknown"
    position = -1
    found = ""
    for symbol, name in VERDICT_SYMBOLS:
        index = text.find(symbol)
        if index >= 0 and (position < 0 or index < position):
            position, verdict, found = index, name, symbol
    if position >= 0:
        text = (text[:position] + text[position + len(found):]).strip()
    if text.startswith("(") and text.endswith(")"):
        text = text[1:-1].strip()
    return verdict, text


def normalize_website(value: str) -> str:
    """
    The host the checks run against: "https://Example.com:8443/path" and
    "example.com" both give "example.com". Each check builds its own URLs
    from a bare host.
    """
    raw = (value or "").strip()
    if not raw:
        raise ValueError("website is empty")
    host = urlsplit(raw if "://" in raw else f"//{raw}").hostname
    if not host or any(c.isspace() for c in host):
        raise ValueError(f"not a domain or URL: {raw!r}")
    return host.rstrip(".").lower()


def summarize(verdicts: Iterable[str]) -> dict:
    """Counts per verdict, and the pass rate among checks with a verdict."""
    counts = {verdict: 0 for verdict in VERDICTS}
    for verdict in verdicts:
        counts[verdict if verdict in counts else "unknown"] += 1
    with_verdict = counts["pass"] + counts["warn"] + counts["fail"]
    return {
        "total": sum(counts.values()),
        "passed": counts["pass"],
        "warnings": counts["warn"],
        "failed": counts["fail"],
        "no_verdict": counts["unknown"],
        "pass_rate_percent": round(counts["pass"] * 100 / with_verdict) if with_verdict else None,
    }
