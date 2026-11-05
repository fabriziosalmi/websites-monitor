"""
The check runner backed by the functions in checks/check_<id>.py.

This table is the only registry of checks. It replaces two that disagreed:
the API's CHECK_MODULES and main.py's WebsiteMonitor list, which used other
names, other arguments and other timeouts for the same functions.
"""
from __future__ import annotations

import asyncio
import importlib
import inspect
import logging
import os
from typing import Callable, Optional

from ..domain import CheckSpec

logger = logging.getLogger(__name__)

# (id, category, name, minimum timeout in seconds or None), in catalog order.
# Names match check.<id>.name in docs/assets/locales/en.json
# (tests/test_registry.py checks it).
REGISTRY = (
    ("ssl_cert", "security", "SSL certificate", None),
    ("ssl_cipher_strength", "security", "TLS cipher strength", None),
    ("security_headers", "security", "Security headers", None),
    ("hsts", "security", "HSTS", None),
    ("xss_protection", "security", "XSS protection", None),
    ("cors_headers", "security", "CORS policy", None),
    ("mixed_content", "security", "Mixed content", None),
    ("subresource_integrity", "security", "Subresource integrity", None),
    ("rate_limiting", "security", "Rate limiting", None),
    ("data_leakage", "security", "Data leakage", None),
    ("pagespeed_performances", "performance", "PageSpeed score", 60),
    ("website_load_time", "performance", "Load time", None),
    ("server_response_time", "performance", "Server response time", None),
    ("brotli_compression", "performance", "Brotli compression", None),
    ("asset_minification", "performance", "Asset minification", None),
    ("cdn", "performance", "CDN", None),
    ("redirect_chains", "performance", "Redirect chains", None),
    ("redirects", "performance", "HTTPS redirect", None),
    ("sitemap", "seo", "Sitemap", None),
    ("robot_txt", "seo", "robots.txt", None),
    ("open_graph_protocol", "seo", "Open Graph tags", None),
    ("alt_tags", "seo", "Image alt text", None),
    ("semantic_markup", "seo", "Semantic markup", None),
    ("url_canonicalization", "seo", "Canonical URL", None),
    ("favicon", "seo", "Favicon", None),
    ("broken_links", "seo", "Broken links", None),
    ("external_links", "seo", "External links", None),
    ("domain_expiration", "domain", "Domain expiration", None),
    ("dnssec", "domain", "DNSSEC", None),
    ("dns_blacklist", "domain", "DNS blocklists", 45),
    ("domain_breach", "domain", "Breach exposure", None),
    ("domainsblacklists_blacklist", "domain", "Domain blocklists", None),
    ("subdomain_enumeration", "domain", "Subdomains", None),
    ("email_domain", "domain", "Email records", None),
    ("cookie_policy", "privacy", "Cookie policy", None),
    ("cookie_flags", "privacy", "Cookie flags", None),
    ("cookie_duration", "privacy", "Cookie duration", None),
    ("cookie_samesite_attribute", "privacy", "Cookie SameSite", None),
    ("ad_and_tracking", "privacy", "Ads and tracking", None),
    ("floc", "privacy", "FLoC opt-out", None),
    ("privacy_exposure", "privacy", "Privacy exposure", None),
    ("privacy_protected_whois", "privacy", "WHOIS privacy", None),
    ("third_party_requests", "privacy", "Third-party requests", None),
    ("third_party_resources", "privacy", "Third-party resources", None),
    ("accessibility", "accessibility", "Accessibility", None),
    ("mobile_friendly", "accessibility", "Mobile friendly", None),
    ("amp_compatibility", "accessibility", "AMP", None),
    ("internationalization", "accessibility", "Internationalization", None),
    ("browser_compatibility", "accessibility", "Browser compatibility", None),
    ("content_type_headers", "technical", "Content-Type header", None),
    ("cms_used", "technical", "CMS detection", None),
    ("clientside_rendering", "technical", "Client-side rendering", None),
    ("deprecated_libraries", "technical", "Deprecated libraries", None),
)

# Requests the rate limiting check sends; the web UI has always used 10.
RATE_LIMITING_REQUESTS = 10


def _first_paragraph(doc: Optional[str]) -> str:
    return " ".join((doc or "").strip().split("\n\n")[0].split())


class PythonCheckRunner:
    """Runs check_<id>(website) from checks/check_<id>.py in a worker thread."""

    def __init__(self, functions: Optional[dict[str, Callable[..., str]]] = None):
        self._functions = functions if functions is not None else self._load()
        self._specs = [
            CheckSpec(
                id=check_id,
                name=name,
                category=category,
                description=_first_paragraph(inspect.getdoc(self._functions[check_id])),
                min_timeout=min_timeout,
            )
            for check_id, category, name, min_timeout in REGISTRY
            if check_id in self._functions
        ]

    @staticmethod
    def _load() -> dict[str, Callable[..., str]]:
        functions = {}
        for check_id, *_ in REGISTRY:
            try:
                module = importlib.import_module(f"checks.check_{check_id}")
                functions[check_id] = getattr(module, f"check_{check_id}")
            except (ImportError, AttributeError) as e:
                # A missing check is left out of the catalog, not a crash.
                logger.warning(f"Could not load check {check_id}: {e}")
        return functions

    def specs(self) -> list[CheckSpec]:
        return list(self._specs)

    async def run(self, check_id: str, website: str, *, pagespeed_api_key: Optional[str] = None) -> str:
        function = self._functions[check_id]
        kwargs: dict = {}
        if check_id in ("pagespeed_performances", "accessibility"):
            kwargs["api_key"] = pagespeed_api_key or os.environ.get("PAGESPEED_API_KEY") or None
        elif check_id == "rate_limiting":
            kwargs["num_requests"] = RATE_LIMITING_REQUESTS
        if inspect.iscoroutinefunction(function):
            return await function(website, **kwargs)
        # Checks are blocking: in a thread they do not stall the event loop,
        # so /health and other requests keep answering during a scan.
        return await asyncio.to_thread(function, website, **kwargs)
