"""check_dns_blacklist tells a DNSBL listing from a DNSBL error code.

Spamhaus answers 127.255.255.252/254/255 when it refuses a query (typo in the
zone, query through a public resolver, rate limit). Those answers were counted
as listings, so every site looked listed in zen.spamhaus.org (🔴).
Nothing here touches the network: socket and the DNS resolver are faked.
"""
import pytest
from dns.resolver import NXDOMAIN

import checks.check_dns_blacklist as mod


def install_fake_dns(monkeypatch, answers):
    """answers: {blacklist zone: [A records]}; other zones answer NXDOMAIN."""
    monkeypatch.setattr(mod.socket, "gethostbyname", lambda domain: "93.184.215.14")

    class FakeResolver:
        def __init__(self, *args, **kwargs):
            self.timeout = None
            self.lifetime = None

        def resolve(self, qname, rdtype):
            assert qname.startswith("14.215.184.93."), qname
            zone = qname[len("14.215.184.93."):]
            if zone in answers:
                return list(answers[zone])
            raise NXDOMAIN()

    monkeypatch.setattr(mod.dns.resolver, "Resolver", FakeResolver)


@pytest.mark.parametrize("code", ["127.255.255.252", "127.255.255.254", "127.255.255.255"])
def test_spamhaus_error_code_is_not_a_listing(monkeypatch, code):
    install_fake_dns(monkeypatch, {"zen.spamhaus.org": [code], "pbl.spamhaus.org": [code]})
    result = mod.check_dns_blacklist("example.com")
    assert result.startswith("🟢"), result
    assert "zen.spamhaus.org" in result  # named as "no verdict", not as listed


def test_zen_sbl_code_is_a_listing(monkeypatch):
    install_fake_dns(monkeypatch, {"zen.spamhaus.org": ["127.0.0.2"]})
    assert mod.check_dns_blacklist("example.com") == "🔴"


def test_zen_pbl_code_is_policy_not_a_threat(monkeypatch):
    install_fake_dns(monkeypatch, {"zen.spamhaus.org": ["127.0.0.10"]})
    assert mod.check_dns_blacklist("example.com") == "🟢"


def test_no_list_answered_gives_no_verdict(monkeypatch):
    install_fake_dns(monkeypatch, {zone: ["127.255.255.254"] for zone in [
        "zen.spamhaus.org", "bl.spamcop.net", "pbl.spamhaus.org", "dnsbl.sorbs.net",
        "b.barracudacentral.org", "dnsbl.dronebl.org",
    ]})
    assert mod.check_dns_blacklist("example.com") == "⚪ (no blacklist answered)"


@pytest.mark.parametrize("blacklist,codes,expected", [
    ("zen.spamhaus.org", ["127.255.255.254"], "error"),
    ("zen.spamhaus.org", ["127.0.0.2"], "listed"),
    ("zen.spamhaus.org", ["127.0.0.4", "127.0.0.10"], "listed"),
    ("zen.spamhaus.org", ["127.0.0.11"], "policy"),
    ("bl.spamcop.net", ["127.0.0.2"], "listed"),
    ("bl.spamcop.net", ["127.0.0.1"], "error"),
    ("bl.spamcop.net", ["192.0.2.1"], "error"),  # NXDOMAIN-hijacking resolver
])
def test_interpret_dnsbl_answer(blacklist, codes, expected):
    assert mod.interpret_dnsbl_answer(blacklist, codes) == expected
