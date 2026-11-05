"""docs/openapi.json matches the API the code defines."""
import pathlib

from scripts.export_openapi import render

SNAPSHOT = pathlib.Path(__file__).resolve().parent.parent / "docs" / "openapi.json"


def test_the_published_openapi_snapshot_is_current():
    assert SNAPSHOT.read_text(encoding="utf-8") == render(), (
        "docs/openapi.json is out of date: run python scripts/export_openapi.py"
    )
