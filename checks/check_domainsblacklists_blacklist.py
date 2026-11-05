import logging
import os
import re
import tempfile
import threading
import time

import requests
from requests.exceptions import RequestException, Timeout, HTTPError

logger = logging.getLogger(__name__)

BLACKLIST_URL = "https://github.com/fabriziosalmi/blacklists/releases/download/latest/blacklist.txt"
CACHE_TTL = 3600
CACHE_PATH = os.path.join(
    os.environ.get("WM_CACHE_DIR", os.path.join(tempfile.gettempdir(), "websites-monitor")),
    "domainsblacklists.txt",
)
_download_lock = threading.Lock()


def _download() -> None:
    """Download the list next to CACHE_PATH, then move it into place."""
    directory = os.path.dirname(CACHE_PATH)
    os.makedirs(directory, exist_ok=True)
    # A process killed mid-download leaves its .part file behind: 107 MB each.
    for name in os.listdir(directory):
        stale = os.path.join(directory, name)
        if name.endswith(".part") and time.time() - os.path.getmtime(stale) > 600:
            try:
                os.unlink(stale)
            except OSError:
                pass
    logger.info("Downloading fresh blacklist data")
    fd, partial = tempfile.mkstemp(dir=directory, suffix=".part")
    try:
        with os.fdopen(fd, "wb") as out, requests.get(
            BLACKLIST_URL,
            headers={"User-Agent": "DomainBlacklistChecker/2.0"},
            stream=True,
            timeout=60,
        ) as response:
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=1 << 20):
                out.write(chunk)
        os.replace(partial, CACHE_PATH)
    except BaseException:
        try:
            os.unlink(partial)
        except OSError:
            pass
        raise


def _refresh_in_background() -> None:
    try:
        _download()
    except Exception as e:
        logger.warning(f"Blacklist refresh failed, keeping the previous copy: {e}")
    finally:
        _download_lock.release()


def _blacklist_file() -> str:
    """
    Path to a local copy of the blacklist.

    The list has about 5.5 million lines (107 MB). Loaded into a Python set
    it took 916 MB of RSS, and the kernel killed the 256 MB API container in
    the middle of a scan. On disk and scanned line by line, memory stays
    flat whatever the size of the list.

    The download takes 20 to 30 seconds, as long as a check's default
    timeout. Only the very first one is waited for: once a copy exists, an
    expired one is still used while a background thread fetches the next.
    """
    if not os.path.exists(CACHE_PATH):
        with _download_lock:
            if not os.path.exists(CACHE_PATH):
                _download()
        return CACHE_PATH
    expired = time.time() - os.path.getmtime(CACHE_PATH) >= CACHE_TTL
    if expired and _download_lock.acquire(blocking=False):
        threading.Thread(target=_refresh_in_background, daemon=True).start()
    return CACHE_PATH


def prefetch_blacklist() -> None:
    """Fetch the list ahead of the first scan; failures only get logged."""
    try:
        _blacklist_file()
    except Exception as e:
        logger.warning(f"Blacklist prefetch failed: {e}")


def check_domainsblacklists_blacklist(domain: str) -> str:
    """
    Check if a domain is present in a large blacklist file hosted online.

    Args:
        domain (str): The domain to check against the blacklist.

    Returns:
        str: 
            - "🔴" if the domain is found in the blacklist
            - "🟢" if the domain is not found in the blacklist
            - "⚪" if an error occurs
    """
    # Input validation and normalization
    if not domain:
        logger.error("Domain is required")
        return "⚪"
    
    # Normalize domain
    domain = domain.lower().strip()
    domain = re.sub(r'^https?://', '', domain)
    domain = re.sub(r'^www\.', '', domain)
    domain = domain.split('/')[0]  # Remove path if present
    domain = domain.split(':')[0]  # Remove port if present
    
    # Validate domain format
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]$', domain):
        logger.error(f"Invalid domain format: {domain}")
        return "⚪"

    # The domain and its parents, without the TLD alone.
    parts = domain.split('.')
    candidates = {'.'.join(parts[i:]) for i in range(len(parts) - 1)}
    candidates = {c for c in candidates if len(c) > 3} or {domain}

    try:
        with open(_blacklist_file(), encoding="utf-8", errors="ignore") as listing:
            for line in listing:
                entry = line.strip().lower()
                if entry in candidates:
                    logger.warning(f"Domain {entry} found in blacklist (original: {domain})")
                    return "🔴"

        logger.info(f"Domain {domain} not found in blacklist")
        return "🟢"

    except (Timeout, HTTPError) as e:
        logger.error(f"HTTP error while checking domain {domain} against blacklist: {e}")
        return "⚪"
    except RequestException as e:
        logger.error(f"Request error while checking domain {domain} against blacklist: {e}")
        return "⚪"
    except Exception as e:
        logger.error(f"Unexpected error while checking domain {domain} against blacklist: {e}")
        return "⚪"
