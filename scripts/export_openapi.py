"""Write docs/openapi.json, the API description the static Swagger page loads.

GitHub Pages serves docs/ without the API behind it, so swagger.html falls
back to this snapshot there. tests/test_openapi_snapshot.py fails when the
snapshot no longer matches the code; run this script to refresh it:

    python scripts/export_openapi.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import api  # noqa: E402


def render() -> str:
    return json.dumps(api.app.openapi(), indent=2, ensure_ascii=False, sort_keys=True) + "\n"


if __name__ == "__main__":
    (ROOT / "docs" / "openapi.json").write_text(render(), encoding="utf-8")
    print("wrote docs/openapi.json")
