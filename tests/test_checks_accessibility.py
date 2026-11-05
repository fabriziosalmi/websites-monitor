"""check_accessibility falls back to local heuristics when Lighthouse fails.

Without a key PageSpeed answers 429; the check then called WAVE with a
placeholder key, WAVE answered 200 with an error body and
wave_data['categories'] raised KeyError: the check crashed instead of
running the heuristics. Nothing here touches the network: requests.get is faked.
"""
import pytest
import requests

import checks.check_accessibility as mod

PAGE = """<!doctype html><html lang="en"><head><title>t</title></head>
<body><h1>Title</h1><img src="a.png" alt="a picture"><p>text</p></body></html>"""
# Heuristic score of PAGE: alt text 0.25 + lang 0.15 + headings 0.15
# + no forms 0.15 = 0.70 (no ARIA, skip link or focus style) -> 🟠
HEURISTIC = "🟠 (heuristic)"


class FakeResponse:
    def __init__(self, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json = json_data
        self.text = text

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Client Error", response=self)

    def json(self):
        if self._json is None:
            raise ValueError("no JSON")
        return self._json


def install_fake_get(monkeypatch, lighthouse, wave=None):
    calls = []

    def fake_get(url, params=None, headers=None, timeout=None):
        calls.append((url, dict(params or {})))
        if "pagespeedonline" in url:
            return lighthouse
        if "wave.webaim.org" in url:
            return wave
        return FakeResponse(200, text=PAGE)

    monkeypatch.setattr(mod.requests, "get", fake_get)
    return calls


@pytest.fixture(autouse=True)
def no_keys(monkeypatch):
    monkeypatch.delenv("PAGESPEED_API_KEY", raising=False)
    monkeypatch.delenv("WAVE_API_KEY", raising=False)


@pytest.mark.parametrize("lighthouse", [
    FakeResponse(429, json_data={"error": {"code": 429}}),
    FakeResponse(200, json_data={"lighthouseResult": {}}),  # no 'categories'
    FakeResponse(200, json_data=None),  # not JSON
], ids=["429", "missing-categories", "not-json"])
def test_api_failure_falls_back_to_heuristics(monkeypatch, lighthouse):
    calls = install_fake_get(monkeypatch, lighthouse)
    assert mod.check_accessibility("example.com") == HEURISTIC
    # WAVE is only tried when WAVE_API_KEY is set
    assert not any("wave.webaim.org" in url for url, _ in calls)


def test_wave_error_body_falls_back_to_heuristics(monkeypatch):
    monkeypatch.setenv("WAVE_API_KEY", "wave-test-key")
    install_fake_get(
        monkeypatch,
        FakeResponse(429),
        wave=FakeResponse(200, json_data={"status": {"success": False, "error": "Invalid key"}}),
    )
    assert mod.check_accessibility("https://example.com/") == HEURISTIC


def test_lighthouse_score_used_with_key_from_env(monkeypatch):
    monkeypatch.setenv("PAGESPEED_API_KEY", "psi-test-key")
    calls = install_fake_get(monkeypatch, FakeResponse(200, json_data={
        "lighthouseResult": {"categories": {"accessibility": {"score": 0.85}}}}))
    assert mod.check_accessibility("example.com") == "🟠"
    assert calls[0][1].get("key") == "psi-test-key"
