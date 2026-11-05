"""DNS-based checks use the dnspython 2.x API and survive resolver refusals.

- check_email_domain passed timeout= to dns.resolver.resolve(), which only
  accepts lifetime=: TypeError, ⚪ for every domain.
- check_dnssec queried qtype RRSIG directly; recursive resolvers answer that
  with SERVFAIL, dnspython raises NoNameservers and the whole check gave ⚪,
  even for signed zones such as example.com.
Nothing here touches the network: the resolver is faked.
"""
from types import SimpleNamespace

import dns.rdatatype
import pytest
from dns.resolver import NoAnswer, NoNameservers

import checks.check_dnssec as dnssec
import checks.check_email_domain as email_domain


def resolve_signature(qname, rdtype="A", rdclass="IN", tcp=False, source=None,
                      raise_on_no_answer=True, source_port=0, lifetime=None, search=None):
    """Same keyword arguments as dnspython 2.x dns.resolver.resolve()."""
    return qname, rdtype, lifetime


def test_email_domain_uses_dnspython2_signature(monkeypatch):
    def fake_resolve(*args, **kwargs):
        resolve_signature(*args, **kwargs)  # TypeError on unknown keywords
        return ['"v=spf1 include:_spf.example.net mx -all"']

    monkeypatch.setattr(email_domain.dns.resolver, "resolve", fake_resolve)
    assert email_domain.check_email_domain("example.com") == "🟢"


def install_fake_dnssec(monkeypatch, signed=True, servfail=False):
    def fake_resolve(qname, rdtype, tcp=False, **kwargs):
        if servfail or rdtype == "RRSIG":  # what 1.1.1.1/8.8.8.8 do for qtype RRSIG
            raise NoNameservers()
        if not signed:
            raise NoAnswer()
        return [object()]

    class FakeResolver:
        def __init__(self, *args, **kwargs):
            pass

        def use_edns(self, *args, **kwargs):
            pass

        def resolve(self, qname, rdtype, tcp=False, **kwargs):
            if servfail:
                raise NoNameservers()
            answer = [SimpleNamespace(rdtype=dns.rdatatype.A)]
            if signed:
                answer.append(SimpleNamespace(rdtype=dns.rdatatype.RRSIG))
            return SimpleNamespace(response=SimpleNamespace(answer=answer))

    monkeypatch.setattr(dnssec.dns.resolver, "resolve", fake_resolve)
    monkeypatch.setattr(dnssec.dns.resolver, "Resolver", FakeResolver)


def test_dnssec_signed_zone_is_green(monkeypatch):
    install_fake_dnssec(monkeypatch, signed=True)
    assert dnssec.check_dnssec("example.com") == "🟢"


def test_dnssec_unsigned_zone_is_red(monkeypatch):
    install_fake_dnssec(monkeypatch, signed=False)
    assert dnssec.check_dnssec("example.com") == "🔴"


def test_dnssec_all_queries_refused_gives_no_verdict(monkeypatch):
    install_fake_dnssec(monkeypatch, servfail=True)
    assert dnssec.check_dnssec("example.com") == "⚪"
