"""check_external_links only calls a link broken on a 4xx (not 429) or 5xx answer.

A rate limit (429) or an exception (timeout, connection reset) says nothing
about the link: they were reported as broken ("Status: None") or as warnings.
Nothing here touches the network: requests.get and requests.head are faked.
"""
import pytest
import requests

import checks.check_external_links as mod


class FakeResponse:
    def __init__(self, status_code, text=""):
        self.status_code = status_code
        self.text = text

    def raise_for_status(self):
        pass

    def close(self):
        pass


def install_fake_http(monkeypatch, link_answers):
    html = "".join(f'<a href="{url}">x</a>' for url in link_answers)

    def answer(url):
        value = link_answers[url]
        if isinstance(value, Exception):
            raise value
        return FakeResponse(value)

    def fake_get(url, **kwargs):
        if url == "https://example.com":
            return FakeResponse(200, text=f"<html><body>{html}</body></html>")
        return answer(url + "#get") if url + "#get" in link_answers else answer(url)

    monkeypatch.setattr(mod.requests, "get", fake_get)
    monkeypatch.setattr(mod.requests, "head", lambda url, **kwargs: answer(url))


def test_rate_limit_and_exceptions_are_not_broken(monkeypatch):
    install_fake_http(monkeypatch, {
        "https://ok.test/": 200,
        "https://limited.test/": 429,
        "https://reset.test/": requests.exceptions.ConnectionError("reset"),
        "https://slow.test/": requests.exceptions.Timeout("slow"),
    })
    assert mod.check_external_links("example.com") == "🟢 (3 links not verified)"


@pytest.mark.parametrize("status", [404, 410, 500, 503])
def test_4xx_and_5xx_are_broken(monkeypatch, status):
    install_fake_http(monkeypatch, {"https://ok.test/": 200, "https://gone.test/": status})
    assert mod.check_external_links("example.com") == "🔴"


def test_head_not_allowed_is_retried_with_get(monkeypatch):
    install_fake_http(monkeypatch, {"https://nohead.test/": 405, "https://nohead.test/#get": 200})
    assert mod.check_external_links("example.com") == "🟢"


def test_nothing_verified_gives_no_verdict(monkeypatch):
    install_fake_http(monkeypatch, {"https://limited.test/": 429})
    assert mod.check_external_links("example.com") == "⚪ (1 links not verified)"
