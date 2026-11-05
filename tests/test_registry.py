"""The one registry of checks, and how the runner calls them."""
import asyncio
import json
import pathlib
import threading

from websites_monitor.adapters import checks as registry
from websites_monitor.adapters.checks import REGISTRY, PythonCheckRunner
from websites_monitor.domain import CATEGORIES

ROOT = pathlib.Path(__file__).resolve().parent.parent
EN = json.loads((ROOT / "docs" / "assets" / "locales" / "en.json").read_text(encoding="utf-8"))
CHECK_FILES = sorted(p.stem[len("check_"):] for p in (ROOT / "checks").glob("check_*.py"))


def test_every_check_module_is_registered_once():
    ids = [row[0] for row in REGISTRY]
    assert len(ids) == len(set(ids))
    assert sorted(ids) == CHECK_FILES


def test_every_check_loads_and_has_a_description():
    runner = PythonCheckRunner()
    specs = runner.specs()
    assert len(specs) == len(REGISTRY)
    assert all(spec.description for spec in specs), [s.id for s in specs if not s.description]


def test_names_and_categories_match_the_web_ui():
    for check_id, category, name, _ in REGISTRY:
        assert category in CATEGORIES
        assert EN[f"check.{check_id}.name"] == name, check_id


def test_the_runner_passes_the_pagespeed_key_and_the_rate_limit_and_uses_a_thread():
    seen = {}

    def pagespeed(website, api_key=None):
        seen["pagespeed"] = (website, api_key, threading.current_thread() is threading.main_thread())
        return "ok"

    def rate_limiting(website, num_requests=5):
        seen["rate_limiting"] = (website, num_requests)
        return "ok"

    def plain(website):
        seen["plain"] = website
        return "ok"

    runner = PythonCheckRunner({"pagespeed_performances": pagespeed, "rate_limiting": rate_limiting, "hsts": plain})
    asyncio.run(runner.run("pagespeed_performances", "example.com", pagespeed_api_key="k"))
    asyncio.run(runner.run("rate_limiting", "example.com"))
    asyncio.run(runner.run("hsts", "example.com"))

    assert seen["pagespeed"] == ("example.com", "k", False)
    assert seen["rate_limiting"] == ("example.com", registry.RATE_LIMITING_REQUESTS)
    assert seen["plain"] == "example.com"


def test_the_pagespeed_key_falls_back_to_the_environment(monkeypatch):
    seen = {}
    monkeypatch.setenv("PAGESPEED_API_KEY", "from-env")
    runner = PythonCheckRunner({"pagespeed_performances": lambda website, api_key=None: seen.setdefault("key", api_key)})

    asyncio.run(runner.run("pagespeed_performances", "example.com"))

    assert seen["key"] == "from-env"
