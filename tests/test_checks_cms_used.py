"""CMS detection looks at asset URLs, the generator tag and headers only."""
import pytest

from checks import check_cms_used as cms


class FakeResponse:
    def __init__(self, text, headers=None):
        self.text = text
        self.headers = headers or {}

    def raise_for_status(self):
        pass


@pytest.fixture
def serve(monkeypatch):
    def _serve(html, headers=None):
        monkeypatch.setattr(cms.requests, "get", lambda *a, **k: FakeResponse(html, headers))
    return _serve


def test_a_png_favicon_is_not_magento(serve):
    serve('<link rel="icon" type="image/png" href="/favicon.png">')

    assert cms.check_cms_used("example.com") == "⚪ (no CMS detected)"


def test_words_and_text_are_not_evidence(serve):
    serve('<p>We moved from Drupal to a wp-free stack, see shopify docs.</p>'
          '<div class="wp-like-grid"></div>')

    assert cms.check_cms_used("example.com") == "⚪ (no CMS detected)"


@pytest.mark.parametrize("html, headers, expected", [
    ('<script src="/wp-includes/js/jquery.js"></script>', None, "WordPress"),
    ('<meta name="generator" content="Drupal 10 (https://www.drupal.org)">', None, "Drupal"),
    ('<link href="https://cdn.shopify.com/s/files/theme.css" rel="stylesheet">', None, "Shopify"),
    ('<script src="/static/version1712/frontend/Magento/luma/en_US/requirejs/require.js"></script>', None, "Magento"),
    ('<html></html>', {"X-Wix-Request-Id": "1"}, "Wix"),
])
def test_real_evidence_is_detected(serve, html, headers, expected):
    serve(html, headers)

    assert cms.check_cms_used("example.com") == f"🟢 ({expected})"
