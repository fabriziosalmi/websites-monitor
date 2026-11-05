"""The web UI lists exactly the checks the API can run."""
import pathlib
import re

from websites_monitor.adapters.checks import REGISTRY

REGISTRY_IDS = [row[0] for row in REGISTRY]
REGISTRY_CATEGORIES = {row[0]: row[1] for row in REGISTRY}

APP_JS = pathlib.Path(__file__).resolve().parent.parent / "docs" / "assets" / "app.js"


def ui_check_ids():
    source = APP_JS.read_text(encoding="utf-8")
    block = source[source.index("const CHECKS = ["):source.index("].map(([id, cat], order)")]
    return re.findall(r"^\s*\['([a-z_]+)',", block, re.M)


def test_the_ui_catalog_matches_the_api_registry():
    ids = ui_check_ids()
    assert len(ids) == len(set(ids)), "a check is listed twice in docs/assets/app.js"
    assert sorted(ids) == sorted(REGISTRY_IDS), (
        "docs/assets/app.js CHECKS and the registry differ: "
        f"only in the UI {sorted(set(ids) - set(REGISTRY_IDS))}, "
        f"only in the API {sorted(set(REGISTRY_IDS) - set(ids))}"
    )


def ui_categories():
    source = APP_JS.read_text(encoding="utf-8")
    block = source[source.index("const CHECKS = ["):source.index("].map(([id, cat], order)")]
    return dict(re.findall(r"^\s*\['([a-z_]+)', '([a-z]+)'\]", block, re.M))


def test_the_api_files_each_check_where_the_ui_does():
    assert REGISTRY_CATEGORIES == ui_categories()


def test_checks_lists_each_runnable_check_once():
    from fastapi.testclient import TestClient

    import api

    body = TestClient(api.app).get("/checks").json()
    slugs = [c["slug"] for c in body["all_checks"]]

    assert body["total_checks"] == len(REGISTRY_IDS) == len(set(slugs))
    assert sorted(slugs) == sorted(REGISTRY_IDS)
    assert "other" not in body["categories"]
    assert all(c["endpoint"] == f"/check/{c['slug']}" for c in body["all_checks"])
