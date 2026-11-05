"""check_domain_expiration copes with every date shape python-whois returns.

python-whois >= 0.9 returns timezone-aware datetimes; older versions and some
registrars return naive datetimes, lists (mixed) or strings. Subtracting a
naive "now" from an aware date raised "can't subtract offset-naive and
offset-aware datetimes" and the check answered ⚪ for every domain.
Nothing here touches the network: whois.whois is faked.
"""
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

import checks.check_domain_expiration as mod


def fake_whois(expiration_date):
    def _whois(domain):
        return SimpleNamespace(expiration_date=expiration_date, creation_date=None)
    return _whois


IN_200_DAYS_AWARE = datetime.now(timezone.utc) + timedelta(days=200, hours=12)
IN_200_DAYS_NAIVE = datetime.utcnow() + timedelta(days=200, hours=12)


@pytest.mark.parametrize("expiration_date", [
    IN_200_DAYS_AWARE,
    IN_200_DAYS_NAIVE,
    IN_200_DAYS_AWARE.astimezone(timezone(timedelta(hours=-5))),
    [IN_200_DAYS_NAIVE + timedelta(days=30), IN_200_DAYS_AWARE],
    IN_200_DAYS_NAIVE.strftime('%Y-%m-%d %H:%M:%S'),
    IN_200_DAYS_AWARE.isoformat(),
], ids=["aware-utc", "naive", "aware-utc-5", "mixed-list", "string", "iso-string"])
def test_any_date_shape_gives_days_left(monkeypatch, expiration_date):
    monkeypatch.setattr(mod.whois, "whois", fake_whois(expiration_date))
    assert mod.check_domain_expiration("example.com") == "🟢 (200 days left)"


def test_aware_date_close_to_expiry_is_red(monkeypatch):
    soon = datetime.now(timezone.utc) + timedelta(days=5, hours=12)
    monkeypatch.setattr(mod.whois, "whois", fake_whois(soon))
    assert mod.check_domain_expiration("https://example.com/") == "🔴 (5 days left)"


def test_unparseable_date_gives_no_verdict(monkeypatch):
    monkeypatch.setattr(mod.whois, "whois", fake_whois("not a date"))
    assert mod.check_domain_expiration("example.com") == "⚪"
