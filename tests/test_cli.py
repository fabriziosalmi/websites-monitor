"""The command line: one command per operation, with exit codes for CI."""
import json

import pytest

from fakes import make_service
from websites_monitor.adapters.cli import main


def cli(capsys, *argv, **runner_kwargs):
    service, _ = make_service(**runner_kwargs)
    code = main(list(argv), service=service)
    out, err = capsys.readouterr()
    return code, out, err


def test_scan_prints_text_by_default_and_json_on_request(capsys):
    code, out, _ = cli(capsys, "scan", "example.com", "--checks", "ssl_cert,hsts")
    assert code == 0
    assert "PASS  example.com" in out and "FAIL  example.com" in out
    assert "1 passed, 0 warnings, 1 failed" in out

    code, out, _ = cli(capsys, "scan", "example.com", "--checks", "ssl_cert", "--json")
    assert json.loads(out)["results"][0]["detail"] == "50 days left"


@pytest.mark.parametrize("fail_on, checks, expected", [
    ("never", "hsts", 0),
    ("fail", "hsts", 1),
    ("fail", "cdn", 0),
    ("warn", "cdn", 1),
    ("warn", "ssl_cert", 0),
])
def test_fail_on_sets_the_exit_code(capsys, fail_on, checks, expected):
    code, _, _ = cli(capsys, "scan", "example.com", "--checks", checks, "--fail-on", fail_on)
    assert code == expected


def test_errors_exit_3_with_a_message(capsys):
    code, _, err = cli(capsys, "check", "nope", "example.com")
    assert code == 3 and "unknown check 'nope'" in err

    code, _, err = cli(capsys, "scan", "   ")
    assert code == 3 and "website is empty" in err


def test_bad_usage_exits_2(capsys):
    with pytest.raises(SystemExit) as exit_info:
        cli(capsys, "scan")
    assert exit_info.value.code == 2


def test_report_writes_a_file(capsys, tmp_path):
    target = tmp_path / "report.md"
    code, _, err = cli(capsys, "report", "example.com", "--output", str(target), "--timeout", "5",
                       "--config", str(tmp_path / "none.yaml"), slow_seconds=0)
    assert code == 0 and "wrote" in err
    assert target.read_text().startswith("# Website Monitor report")


def test_checks_and_health(capsys):
    code, out, _ = cli(capsys, "checks", "--category", "security")
    assert code == 0 and "ssl_cert" in out and "cdn" not in out
    code, out, _ = cli(capsys, "health")
    assert out.strip() == "healthy, version 9.9.9, 5 checks"
