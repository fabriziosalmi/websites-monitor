"""check_mobile_friendly runs locally from the page HTML with one argument.

It required an api_key positional argument that WebsiteMonitor never passes
(TypeError on every run). Nothing here touches the network: requests.get is faked.
"""
import pytest

import checks.check_mobile_friendly as mod


class FakeResponse:
    status_code = 200

    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        pass


def page(head="", body="<p>hi</p>"):
    return f"<!doctype html><html><head>{head}</head><body>{body}</body></html>"


RESPONSIVE = '<meta name="viewport" content="width=device-width, initial-scale=1">'


@pytest.mark.parametrize("html,expected", [
    (page(RESPONSIVE), "🟢"),
    (page(RESPONSIVE + "<style>.c{max-width:1200px}</style>"), "🟢"),
    (page(), "🔴 (no responsive viewport meta)"),
    (page('<meta name="viewport" content="width=1024">'), "🔴 (no responsive viewport meta)"),
    (page('<meta name="viewport" content="width=device-width, user-scalable=no">'), "🟡 (zoom disabled)"),
    (page(RESPONSIVE + "<style>body{width: 1200px}</style>"),
     "🟡 (1 fixed-width element(s) >= 980px)"),
    (page(RESPONSIVE, '<table width="1024"><tr><td>x</td></tr></table>'),
     "🟡 (1 fixed-width element(s) >= 980px)"),
], ids=["responsive", "max-width-ok", "no-viewport", "fixed-viewport", "zoom-off",
        "fixed-css", "fixed-attr"])
def test_mobile_friendly_criteria(monkeypatch, html, expected):
    monkeypatch.setattr(mod.requests, "get", lambda url, **kwargs: FakeResponse(html))
    assert mod.check_mobile_friendly("example.com") == expected
