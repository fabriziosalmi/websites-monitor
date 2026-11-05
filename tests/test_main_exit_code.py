"""main.py fails loudly: the scheduler only sees its exit code."""
import asyncio

import pytest

import main


def test_a_critical_error_exits_non_zero(monkeypatch):
    def broken_config(*args, **kwargs):
        raise OSError("config.yaml unreadable")

    monkeypatch.setattr(main, "load_config", broken_config)

    with pytest.raises(SystemExit) as exit_info:
        asyncio.run(main.main())
    assert exit_info.value.code == 1


def test_a_missing_template_still_writes_the_report(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = main.Config(websites=["example.com"], output_file="report.md", report_template="missing.md")

    main.generate_report(config, [("HSTS", ["🟢"])])

    report = (tmp_path / "report.md").read_text()
    assert "\nexample.com | 🟢 |" in report


def test_the_report_has_no_usage_guide_and_uses_the_template(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "usage.md").write_text("USAGE GUIDE")
    (tmp_path / "tpl.md").write_text("Checked daily.\n")
    config = main.Config(websites=["a.test", "b.test"], output_file="out.md", report_template="tpl.md")

    main.generate_report(config, [("HSTS", ["🟢", "🔴"]), ("CDN", ["🟡", "⚪"])])

    report = (tmp_path / "out.md").read_text()
    assert report.startswith("# Website Monitor report\n\nChecked daily.\n\nGenerated on ")
    assert "USAGE GUIDE" not in report
    assert "| Website | HSTS | CDN |" in report
    assert "\na.test | 🟢 | 🟡 |" in report and "\nb.test | 🔴 | ⚪ |" in report


def test_output_file_can_come_from_the_environment(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "config.yaml").write_text("websites: [a.test]\noutput_file: README.md\n")
    monkeypatch.setenv("OUTPUT_FILE", "reports/report.md")

    assert main.load_config().output_file == "reports/report.md"
