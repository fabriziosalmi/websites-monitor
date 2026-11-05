"""main.py writes the report for config.yaml and fails loudly."""
import main
from fakes import make_service


def test_main_writes_the_report_with_the_template(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "config.yaml").write_text("websites: [a.test, b.test]\ntimeout: 5\noutput_file: out.md\nreport_template: tpl.md\n")
    (tmp_path / "tpl.md").write_text("Checked daily.\n")
    service, _ = make_service(slow_seconds=0)
    monkeypatch.setattr(main, "build_service", lambda config: service)

    assert main.main() == 0

    report = (tmp_path / "out.md").read_text()
    assert report.startswith("# Website Monitor report\n\nChecked daily.\n\nGenerated on ")
    assert "| a.test |" in report and "| b.test |" in report


def test_output_file_can_come_from_the_environment(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "config.yaml").write_text("websites: [a.test]\noutput_file: README.md\n")
    (tmp_path / "reports").mkdir()
    monkeypatch.setenv("OUTPUT_FILE", "reports/report.md")
    service, _ = make_service(slow_seconds=0)
    monkeypatch.setattr(main, "build_service", lambda config: service)

    assert main.main() == 0
    assert (tmp_path / "reports" / "report.md").exists()
    assert not (tmp_path / "README.md").exists()


def test_a_failure_exits_1(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    def broken(config):
        raise OSError("disk full")

    monkeypatch.setattr(main, "build_service", broken)

    assert main.main() == 1
