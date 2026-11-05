"""The REST API translates HTTP to MonitorService and back."""
from fastapi.testclient import TestClient

from fakes import make_service
from websites_monitor.adapters.http import create_app


def client(slow_seconds=0):
    service, runner = make_service(slow_seconds=slow_seconds)
    return TestClient(create_app(service)), runner


def test_post_monitor_single_runs_each_check_once_for_the_host():
    c, runner = client()

    body = c.post("/monitor/single", json={"website": "https://Example.com/x", "checks": ["hsts", "cdn", "hsts"]}).json()

    assert [r["check_id"] for r in body["results"]] == ["hsts", "cdn"]
    assert body["website"] == "example.com"
    assert [r["verdict"] for r in body["results"]] == ["fail", "warn"]
    assert [call[:2] for call in runner.calls] == [("hsts", "example.com"), ("cdn", "example.com")]


def test_get_monitor_single_runs_everything_with_the_same_response_shape():
    c, _ = client()

    body = c.get("/monitor/single", params={"website": "example.com", "timeout": 5}).json()

    assert body["checks_performed"] == 5
    assert set(body) == {"success", "message", "website", "results", "summary", "execution_time", "timestamp",
                         "websites_checked", "checks_performed"}


def test_a_timeout_and_an_exception_come_back_as_no_verdict():
    c, _ = client(slow_seconds=10)

    body = c.post("/monitor/single", json={"website": "example.com", "checks": ["slow", "broken"], "timeout": 5}).json()

    assert [r["error"] for r in body["results"]] == ["Timed out after 5s", "boom"]


def test_a_website_that_is_not_a_host_is_rejected():
    c, _ = client()

    assert c.post("/monitor/single", json={"website": "   ", "checks": ["hsts"]}).status_code == 422
    assert c.get("/monitor/single", params={"website": "   "}).status_code == 422


def test_each_check_has_its_own_endpoint():
    c, runner = client()

    body = c.get("/check/hsts", params={"website": "https://example.com/"}).json()

    assert body["check_id"] == "hsts" and body["verdict"] == "fail" and body["website"] == "example.com"
    assert "execution_time" in body
    assert c.get("/check/nope", params={"website": "example.com"}).status_code == 404


def test_checks_can_be_filtered_by_category():
    c, _ = client()

    assert c.get("/checks", params={"category": "performance"}).json()["total_checks"] == 1
    assert c.get("/checks", params={"category": "nope"}).status_code == 422


def test_report_formats_and_a_bad_one():
    c, _ = client()

    md = c.post("/generate-report", json={"websites": ["example.com"], "output_format": "markdown", "timeout": 5}).json()
    assert md["report_content"].startswith("# Website Monitor report")
    assert c.post("/generate-report", json={"websites": ["example.com"], "output_format": "pdf"}).status_code == 422


def test_root_and_api_redirect_and_swagger_is_vendored():
    c, _ = client()

    assert c.get("/", follow_redirects=False).headers["location"] == "/docs/"
    assert c.get("/api", follow_redirects=False).headers["location"] == "/api/docs"
    page = c.get("/api/docs").text
    assert "/docs/vendor/swagger-ui-bundle.js" in page and "cdn.jsdelivr.net" not in page
    assert c.get("/docs/fonts/inter-5.3.0/inter-latin-wght-normal.woff2").status_code == 200


def test_health_reports_the_service_version():
    c, _ = client()

    assert c.get("/health").json()["version"] == "9.9.9"
