"""POST /monitor/single runs each requested check once and says which one.

The checks are fakes: nothing here touches the network.
"""
import asyncio

import pytest
from fastapi.testclient import TestClient

import api
from main import WebsiteMonitor


class StubMonitor:
    """A WebsiteMonitor whose checks share slugs with CHECK_FUNCTIONS keys."""

    calls = []

    def __init__(self, config):
        def monitor_hsts(website):
            StubMonitor.calls.append(("monitor", "hsts"))
            return "🔴"

        def monitor_ssl_certificate(website):
            StubMonitor.calls.append(("monitor", "ssl_certificate"))
            return "🟢 (50 days left)"

        self.check_functions = [
            WebsiteMonitor.Check("HSTS", monitor_hsts),
            WebsiteMonitor.Check("SSL Certificate", monitor_ssl_certificate),
        ]


@pytest.fixture
def client(monkeypatch):
    calls = []

    def fake_hsts(website):
        calls.append(("individual", "hsts", website))
        return "🟢"

    def fake_cdn(website):
        calls.append(("individual", "cdn", website))
        return "🟡"

    async def fake_slow(website):
        await asyncio.sleep(10)
        return "🟢"

    def fake_broken(website):
        raise ValueError("boom")

    StubMonitor.calls = []
    monkeypatch.setattr(api, "WebsiteMonitor", StubMonitor)
    monkeypatch.setattr(api, "CHECK_FUNCTIONS", {
        "hsts": fake_hsts,
        "cdn": fake_cdn,
        "slow": fake_slow,
        "broken": fake_broken,
    })
    test_client = TestClient(api.app)
    test_client.calls = calls
    return test_client


def run(client, checks, timeout=30):
    response = client.post("/monitor/single", json={
        "website": "example.com", "checks": checks, "timeout": timeout,
    })
    assert response.status_code == 200, response.text
    return response.json()


def test_a_slug_known_to_both_registries_runs_once(client):
    body = run(client, ["hsts", "cdn", "hsts"])

    assert [r["check_id"] for r in body["results"]] == ["hsts", "cdn"]
    assert body["checks_performed"] == 2
    assert [r["result"] for r in body["results"]] == ["🟢", "🟡"]
    assert client.calls == [
        ("individual", "hsts", "example.com"),
        ("individual", "cdn", "example.com"),
    ]
    assert StubMonitor.calls == []


def test_a_monitor_only_slug_still_runs(client):
    body = run(client, ["ssl_certificate"])

    assert body["results"][0]["check_id"] == "ssl_certificate"
    assert body["results"][0]["check_name"] == "SSL Certificate"
    assert body["results"][0]["result"] == "🟢 (50 days left)"
    assert StubMonitor.calls == [("monitor", "ssl_certificate")]


def test_an_unknown_slug_is_reported_not_dropped(client):
    body = run(client, ["nope"])

    assert body["results"][0]["check_id"] == "nope"
    assert body["results"][0]["status"] == "error"
    assert body["results"][0]["error"] == "Unknown check"


def test_a_timeout_says_so(client):
    body = run(client, ["slow"], timeout=5)

    result = body["results"][0]
    assert result["status"] == "error"
    assert result["result"] == "⚪"
    assert result["error"] == "Timed out after 5s"


def test_an_exception_keeps_its_message(client):
    body = run(client, ["broken"])

    assert body["results"][0]["status"] == "error"
    assert body["results"][0]["error"] == "boom"


def test_root_redirects_to_the_ui_mount(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/docs/"
    assert client.get("/docs/fonts/inter-5.3.0/inter-latin-wght-normal.woff2").status_code == 200


def test_health_reports_the_app_version(client):
    assert client.get("/health").json()["version"] == api.app.version


def test_a_url_is_reduced_to_its_host(client):
    response = client.post("/monitor/single", json={
        "website": "https://Example.com.:8443/path?q=1", "checks": ["hsts"],
    })

    assert response.status_code == 200, response.text
    assert response.json()["results"][0]["website"] == "example.com"
    assert client.calls[-1] == ("individual", "hsts", "example.com")


def test_a_website_that_is_not_a_host_is_rejected(client):
    response = client.post("/monitor/single", json={"website": "   ", "checks": ["hsts"]})

    assert response.status_code == 422


def test_the_single_check_endpoint_gets_a_host_too(client):
    response = client.get("/check/hsts", params={"website": "https://example.com/"})

    assert response.status_code == 200, response.text
    assert response.json()["result"] == "🟢"
    assert client.calls == [("individual", "hsts", "example.com")]
