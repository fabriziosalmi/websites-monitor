"""MonitorService: what every interface returns."""
import asyncio

import pytest

from fakes import FIXED_NOW, make_service
from websites_monitor.application import render_html, render_markdown
from websites_monitor.domain import CheckSpec, parse_result, summarize


def run(coro):
    return asyncio.run(coro)


@pytest.mark.parametrize("raw, verdict, detail", [
    ("\U0001F7E2 (50 days left)", "pass", "50 days left"),
    ("\U0001F7E1", "warn", ""),
    ("\U0001F7E0 (1 found: www.example.com)", "warn", "1 found: www.example.com"),
    ("\U0001F534", "fail", ""),
    ("⚪ (no PageSpeed API key)", "unknown", "no PageSpeed API key"),
    ("91", "unknown", "91"),
    (None, "unknown", ""),
])
def test_a_result_string_gives_a_verdict_and_a_detail(raw, verdict, detail):
    assert parse_result(raw) == (verdict, detail)


def test_the_summary_leaves_checks_without_a_verdict_out_of_the_pass_rate():
    assert summarize(["pass", "pass", "warn", "fail", "unknown"]) == {
        "total": 5, "passed": 2, "warnings": 1, "failed": 1, "no_verdict": 1, "pass_rate_percent": 50,
    }
    assert summarize(["unknown"])["pass_rate_percent"] is None


def test_scan_runs_each_requested_check_once_in_order_against_the_host():
    service, runner = make_service()

    body = run(service.scan("https://Example.com:8443/x", ["hsts", "cdn", "hsts"]))

    assert [r["check_id"] for r in body["results"]] == ["hsts", "cdn"]
    assert [c[:2] for c in runner.calls] == [("hsts", "example.com"), ("cdn", "example.com")]
    assert body["website"] == "example.com"
    assert body["results"][0]["verdict"] == "fail" and body["results"][1]["verdict"] == "warn"
    assert body["summary"] == {"total": 2, "passed": 0, "warnings": 1, "failed": 1, "no_verdict": 0, "pass_rate_percent": 0}
    assert body["checks_performed"] == 2
    assert body["timestamp"] == FIXED_NOW.isoformat()


def test_scan_without_checks_runs_the_whole_catalog():
    service, runner = make_service(slow_seconds=0)

    body = run(service.scan("example.com", timeout=5))

    assert [r["check_id"] for r in body["results"]] == ["ssl_cert", "hsts", "cdn", "slow", "broken"]


def test_an_unknown_check_a_timeout_and_an_exception_are_no_verdict_with_a_reason():
    service, _ = make_service()

    body = run(service.scan("example.com", ["nope", "slow", "broken"], timeout=1))
    by_id = {r["check_id"]: r for r in body["results"]}

    assert by_id["nope"]["error"] == "Unknown check"
    assert by_id["slow"]["error"] == "Timed out after 1s"
    assert by_id["broken"]["error"] == "boom"
    assert all(r["verdict"] == "unknown" and r["status"] == "error" for r in body["results"])


def test_a_check_with_a_longer_minimum_gets_it():
    spec = CheckSpec("pagespeed_performances", "PageSpeed", "performance", "", min_timeout=60)

    assert spec.timeout_for(30) == 60
    assert spec.timeout_for(120) == 120


def test_concurrency_is_bounded():
    service, runner = make_service(slow_seconds=0)

    run(service.scan("example.com", ["ssl_cert", "hsts", "cdn", "slow"], concurrency=2))

    assert runner.max_in_flight == 2


def test_run_check_returns_one_outcome_and_rejects_an_unknown_id():
    service, _ = make_service()

    outcome = run(service.run_check("ssl_cert", "example.com"))

    assert outcome["verdict"] == "pass" and outcome["detail"] == "50 days left"
    assert outcome["execution_time"] == outcome["duration_ms"] / 1000
    with pytest.raises(KeyError):
        run(service.run_check("nope", "example.com"))


def test_a_website_that_is_not_a_host_is_rejected():
    service, _ = make_service()

    with pytest.raises(ValueError):
        run(service.scan("   "))


def test_scan_many_groups_results_by_check():
    service, _ = make_service(slow_seconds=0)

    body = run(service.scan_many(["a.test", "b.test", "a.test"], timeout=5))

    assert body["websites_checked"] == 2
    assert body["checks_performed"] == 10
    first = body["results"][0]
    assert first["check_id"] == "ssl_cert"
    assert [o["website"] for o in first["results"]] == ["a.test", "b.test"]


def test_list_checks_filters_by_category_and_rejects_an_unknown_one():
    service, _ = make_service()

    assert [c["slug"] for c in service.list_checks("security")["all_checks"]] == ["hsts", "ssl_cert"]
    with pytest.raises(ValueError):
        service.list_checks("nope")


def test_the_markdown_report_puts_one_site_per_row_and_escapes_pipes():
    data = {"results": [
        {"check_id": "a", "check_name": "A | B", "results": [{"website": "x.test", "result": "\U0001F7E2 (1|2)"}]},
    ]}

    text = render_markdown(data, FIXED_NOW, "Checked daily.\n")

    assert text.startswith("# Website Monitor report\n\nChecked daily.\n\nGenerated on 2026-11-05 12:00:00 UTC.")
    assert "| Website | A \\| B |" in text
    assert "| x.test | \U0001F7E2 (1\\|2) |" in text


def test_the_html_report_escapes_what_the_scanned_site_returned():
    data = {"websites_checked": 1, "execution_time": 1.0, "results": [
        {"check_id": "a", "check_name": "A", "results": [
            {"website": "x.test", "result": "<script>alert(1)</script>", "verdict": "fail"},
        ]},
    ]}

    page = render_html(data, FIXED_NOW)

    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page


def test_report_rejects_an_unknown_format():
    service, _ = make_service()

    with pytest.raises(ValueError):
        run(service.report(["example.com"], "pdf"))
