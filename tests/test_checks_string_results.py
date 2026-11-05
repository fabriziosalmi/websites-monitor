"""Every check returns a string that starts with its verdict.

subresource_integrity and subdomain_enumeration returned tuples, which the
API sent as JSON arrays and the Markdown report printed as "('🟢', 0)".
"""
from checks import check_subdomain_enumeration as subdomains
from checks import check_subresource_integrity as sri


class FakeResponse:
    def __init__(self, text):
        self.text = text
        self.content = text.encode()
        self.status_code = 200
        self.headers = {"Content-Type": "text/html"}

    def raise_for_status(self):
        pass


def page(monkeypatch, html):
    monkeypatch.setattr(sri.requests, "get", lambda *a, **k: FakeResponse(html))


def test_sri_coverage_is_a_string_with_the_counts(monkeypatch):
    page(monkeypatch, """<html><head>
        <script src="https://cdn.test/a.js" integrity="sha384-x"></script>
        <script src="https://cdn.test/b.js"></script>
    </head></html>""")

    assert sri.check_subresource_integrity("example.com") == "🟠 (1 of 2 external resources with SRI)"


def test_sri_without_external_resources(monkeypatch):
    page(monkeypatch, "<html><head><script>1</script></head></html>")

    assert sri.check_subresource_integrity("example.com") == "🟢 (no external scripts or stylesheets)"


def test_subdomains_are_named_and_capped():
    found = [f"https://s{i}.example.com" for i in range(7)]

    assert subdomains._describe(found, ["https://s0.example.com"]) == (
        "7 found: s0.example.com, s1.example.com, s2.example.com, s3.example.com, "
        "s4.example.com and 2 more; risky: s0.example.com"
    )


def test_subdomain_enumeration_returns_a_string(monkeypatch):
    monkeypatch.setattr(subdomains, "check_subdomain_enumeration", subdomains.check_subdomain_enumeration)
    monkeypatch.setattr(subdomains.requests, "get", lambda *a, **k: (_ for _ in ()).throw(OSError("offline")))
    monkeypatch.setattr(subdomains.requests, "head", lambda *a, **k: (_ for _ in ()).throw(OSError("offline")), raising=False)

    result = subdomains.check_subdomain_enumeration("example.com")

    assert isinstance(result, str)
    assert result[0] in "🟢🟠🔴⚪"
