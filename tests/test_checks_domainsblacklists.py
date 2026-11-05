"""The domain blacklist lives on disk and is never awaited once a copy exists."""
import os
import threading
import time

import pytest

from checks import check_domainsblacklists_blacklist as bl


@pytest.fixture
def cache(tmp_path, monkeypatch):
    path = tmp_path / "domainsblacklists.txt"
    monkeypatch.setattr(bl, "CACHE_PATH", str(path))
    monkeypatch.setattr(bl, "_download_lock", threading.Lock())
    downloads = []

    def fake_download():
        downloads.append(time.time())
        path.write_text("# comment\nbad.example\nevil.test\n")

    monkeypatch.setattr(bl, "_download", fake_download)
    return path, downloads


def test_a_listed_domain_and_its_subdomains_fail(cache):
    assert bl.check_domainsblacklists_blacklist("evil.test") == "🔴"
    assert bl.check_domainsblacklists_blacklist("https://www.shop.evil.test/x") == "🔴"
    assert bl.check_domainsblacklists_blacklist("example.com") == "🟢"


def test_the_first_copy_is_downloaded_once(cache):
    path, downloads = cache

    bl.check_domainsblacklists_blacklist("example.com")
    bl.check_domainsblacklists_blacklist("example.org")

    assert len(downloads) == 1


def test_an_expired_copy_is_used_while_it_refreshes(cache, monkeypatch):
    path, downloads = cache
    path.write_text("old.example\n")
    old = time.time() - bl.CACHE_TTL - 10
    os.utime(path, (old, old))
    release = threading.Event()

    def slow_download():
        release.wait(5)
        downloads.append(time.time())
        path.write_text("new.example\n")

    monkeypatch.setattr(bl, "_download", slow_download)

    started = time.time()
    assert bl.check_domainsblacklists_blacklist("old.example") == "🔴"
    assert time.time() - started < 1, "the check waited for the download"

    release.set()
    for _ in range(50):
        if downloads:
            break
        time.sleep(0.05)
    for _ in range(50):
        if not bl._download_lock.locked():
            break
        time.sleep(0.05)
    assert bl.check_domainsblacklists_blacklist("new.example") == "🔴"


def test_a_failed_refresh_keeps_the_previous_copy(cache, monkeypatch):
    path, _ = cache
    path.write_text("evil.test\n")
    old = time.time() - bl.CACHE_TTL - 10
    os.utime(path, (old, old))
    monkeypatch.setattr(bl, "_download", lambda: (_ for _ in ()).throw(OSError("offline")))

    assert bl.check_domainsblacklists_blacklist("evil.test") == "🔴"
    for _ in range(50):
        if not bl._download_lock.locked():
            break
        time.sleep(0.05)
    assert not bl._download_lock.locked()
    assert path.read_text() == "evil.test\n"


def test_orphan_partial_downloads_are_removed(tmp_path, monkeypatch):
    monkeypatch.setattr(bl, "CACHE_PATH", str(tmp_path / "domainsblacklists.txt"))
    orphan = tmp_path / "abc.part"
    orphan.write_text("half")
    old = time.time() - 3600
    os.utime(orphan, (old, old))

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def raise_for_status(self):
            pass

        def iter_content(self, chunk_size):
            yield b"evil.test\n"

    monkeypatch.setattr(bl.requests, "get", lambda *a, **k: Response())
    bl._download()

    assert not orphan.exists()
    assert (tmp_path / "domainsblacklists.txt").read_text() == "evil.test\n"
    assert not list(tmp_path.glob("*.part"))
