"""Checks that need a key or token answer ⚪ with a reason when it is missing.

WebsiteMonitor calls every check as check(website): check_data_leakage(website,
token) raised TypeError on every run. Nothing here touches the network:
requests is replaced by a function that fails the test if called.
"""
import pytest

import checks.check_data_leakage as data_leakage
import checks.check_pagespeed_performances as pagespeed


def no_network(*args, **kwargs):
    raise AssertionError("the check must not call the network without a key")


def test_data_leakage_without_token(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setattr(data_leakage.requests, "get", no_network)
    assert data_leakage.check_data_leakage("example.com") == "⚪ (GITHUB_TOKEN not set)"


def test_data_leakage_reads_token_from_env(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "gh-test-token")
    seen = []

    def fake_get(url, headers=None, **kwargs):
        seen.append(headers.get("Authorization"))
        raise data_leakage.RequestException("offline")

    monkeypatch.setattr(data_leakage.requests, "get", fake_get)
    data_leakage.check_data_leakage("example.com")
    assert seen and seen[0] == "token gh-test-token"


def test_pagespeed_without_key(monkeypatch):
    monkeypatch.delenv("PAGESPEED_API_KEY", raising=False)
    monkeypatch.setattr(pagespeed.requests, "get", no_network)
    assert pagespeed.check_pagespeed_performances("example.com") == "⚪ (no PageSpeed API key)"


def test_pagespeed_reads_key_from_env(monkeypatch):
    monkeypatch.setenv("PAGESPEED_API_KEY", "psi-test-key")
    seen = []

    class Resp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"lighthouseResult": {"categories": {"performance": {"score": 0.91}}}}

    def fake_get(url, params=None, timeout=None):
        seen.append(params.get("key"))
        return Resp()

    monkeypatch.setattr(pagespeed.requests, "get", fake_get)
    assert pagespeed.check_pagespeed_performances("example.com") == "🟢 (91/100, mobile)"
    assert seen == ["psi-test-key"]


@pytest.mark.parametrize("score, expected", [
    (0.93, "🟢 (93/100, mobile)"),
    (0.90, "🟢 (90/100, mobile)"),
    (0.89, "🟠 (89/100, mobile)"),
    (0.50, "🟠 (50/100, mobile)"),
    (0.49, "🔴 (49/100, mobile)"),
])
def test_pagespeed_score_gets_lighthouse_verdict(monkeypatch, score, expected):
    from checks import check_pagespeed_performances as ps

    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"lighthouseResult": {"categories": {"performance": {"score": score}}}}

    monkeypatch.setattr(ps.requests, "get", lambda *a, **k: Response())

    assert ps.check_pagespeed_performances("example.com", "test-key") == expected
