"""check_browser_compatibility gives no verdict, fast, when no browser can run.

The Docker image has no browser: Selenium Manager downloaded a chromedriver
that could not start (exit 127) and the check answered 🔴 for every site.
Nothing here starts a browser: browser lookup and drivers are faked.
"""
from selenium.common.exceptions import WebDriverException

import checks.check_browser_compatibility as mod


def test_no_browser_installed(monkeypatch):
    def must_not_start(*args, **kwargs):
        raise AssertionError("no driver must be started when no browser is installed")

    monkeypatch.setattr(mod, "_browser_installed", lambda name: False)
    monkeypatch.setattr(mod.webdriver, "Chrome", must_not_start)
    monkeypatch.setattr(mod.webdriver, "Firefox", must_not_start)
    assert mod.check_browser_compatibility("example.com") == "⚪ (no browser available)"


def test_driver_that_cannot_start_is_not_a_verdict(monkeypatch):
    def broken_driver(*args, **kwargs):
        raise WebDriverException("Service chromedriver unexpectedly exited. Status code was: 127")

    monkeypatch.setattr(mod, "_browser_installed", lambda name: True)
    monkeypatch.setattr(mod.webdriver, "Chrome", broken_driver)
    monkeypatch.setattr(mod.webdriver, "Firefox", broken_driver)
    assert mod.check_browser_compatibility("example.com") == "⚪ (no browser available)"
