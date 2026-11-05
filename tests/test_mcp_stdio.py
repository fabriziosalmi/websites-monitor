"""Over stdio, what a check prints goes to stderr, never onto the protocol."""
import pathlib
import subprocess
import sys

CLIENT = pathlib.Path(__file__).resolve().parent / "mcp_stdio_client.py"


def test_printing_checks_do_not_corrupt_the_protocol():
    run = subprocess.run([sys.executable, str(CLIENT)], capture_output=True, text=True, timeout=60)
    output = run.stdout + run.stderr

    assert run.returncode == 0, output
    assert "verdicts: ['pass', 'fail']" in run.stdout
    assert "a check printed this for example.com" in run.stderr
    assert "Invalid JSON" not in output and "ValidationError" not in output, output
