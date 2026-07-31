"""
Playwright-based page fetcher.

The fetcher is a context manager that owns a single browser
instance. Each call to :meth:`Fetcher.fetch` opens a fresh page in
the same context, navigates to the URL and collects the response
data. The fetcher never analyzes anything: it just visits a page
and reports what the browser saw.

Playwright is imported lazily so the rest of the SEO module keeps
loading when the dependency is missing (e.g. in a CI image that
runs unit tests only).
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

log = logging.getLogger(__name__)

if TYPE_CHECKING:  # pragma: no cover
    from playwright.sync_api import Browser, BrowserContext, Playwright


@dataclass
class FetchResult:
    """Everything the fetcher observed on one URL."""

    url: str
    final_url: str
    status_code: int
    response_time_ms: int
    redirect_count: int
    canonical_url: str | None
    content_type: str
    html: str
    title: str = ""
    meta_description: str = ""
    h1: str = ""
    images_total: int = 0
    images_without_alt: int = 0
    is_indexable: bool = True
    internal_links: list[str] = field(default_factory=list)
    external_links: list[str] = field(default_factory=list)
    error: str | None = None


# JavaScript that runs in the page to extract all the SEO-relevant
# bits in a single round-trip.
_PAGE_METADATA_JS = r"""
() => {
    const links = Array.from(document.querySelectorAll('a[href]'))
        .map(a => a.href)
        .filter(h => h && !h.startsWith('javascript:') && !h.startsWith('mailto:'));

    const canonicalEl = document.querySelector('link[rel="canonical"]');
    const robotsEl = document.querySelector('meta[name="robots"]');
    const titleEl = document.querySelector('title');
    const metaEl = document.querySelector('meta[name="description"]');
    const h1El = document.querySelector('h1');
    const imgs = Array.from(document.querySelectorAll('img'));

    return {
        links: links,
        canonical: canonicalEl ? canonicalEl.href : null,
        robots: robotsEl ? (robotsEl.content || '') : '',
        title: titleEl ? (titleEl.textContent || '').trim() : '',
        meta: metaEl ? (metaEl.content || '').trim() : '',
        h1: h1El ? (h1El.textContent || '').trim() : '',
        imagesTotal: imgs.length,
        imagesWithoutAlt: imgs.filter(img => !img.getAttribute('alt')).length,
    };
}
"""


class Fetcher:
    """Owns a Playwright browser context and fetches one URL at a time."""

    def __init__(
        self,
        *,
        base_domain: str,
        timeout_ms: int = 30_000,
        headless: bool = True,
        user_agent: str | None = None,
    ) -> None:
        self.base_domain = base_domain.lower()
        self.timeout_ms = timeout_ms
        self.headless = headless
        self.user_agent = user_agent

        self._pw: "Playwright | None" = None
        self._browser: "Browser | None" = None
        self._context: "BrowserContext | None" = None

    # ------------------------------------------------------------------ #
    # lifecycle
    # ------------------------------------------------------------------ #
    def __enter__(self) -> "Fetcher":
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:  # pragma: no cover - environment check
            raise RuntimeError(
                "Playwright is not installed. Run:\n"
                "  pip install playwright\n"
                "  playwright install chromium"
            ) from exc

        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(headless=self.headless)
        context_kwargs: dict[str, Any] = {"ignore_https_errors": True}
        if self.user_agent:
            context_kwargs["user_agent"] = self.user_agent
        self._context = self._browser.new_context(**context_kwargs)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            if self._context is not None:
                self._context.close()
        finally:
            self._context = None
            if self._browser is not None:
                self._browser.close()
            self._browser = None
            if self._pw is not None:
                self._pw.stop()
            self._pw = None

    # ------------------------------------------------------------------ #
    # public API
    # ------------------------------------------------------------------ #
    def fetch(self, url: str) -> FetchResult:
        if self._context is None:
            raise RuntimeError("Fetcher must be used as a context manager")

        page = self._context.new_page()
        start = time.monotonic()
        try:
            try:
                response = page.goto(
                    url, timeout=self.timeout_ms, wait_until="domcontentloaded"
                )
            except Exception as exc:  # noqa: BLE001 - network/browser errors
                elapsed = int((time.monotonic() - start) * 1000)
                log.warning("Failed to fetch %s: %s", url, exc)
                return FetchResult(
                    url=url,
                    final_url=url,
                    status_code=0,
                    response_time_ms=elapsed,
                    redirect_count=0,
                    canonical_url=None,
                    content_type="",
                    html="",
                    error=str(exc),
                )

            elapsed = int((time.monotonic() - start) * 1000)

            if response is None:
                return FetchResult(
                    url=url,
                    final_url=url,
                    status_code=0,
                    response_time_ms=elapsed,
                    redirect_count=0,
                    canonical_url=None,
                    content_type="",
                    html="",
                    error="No response",
                )

            metadata = self._extract_metadata(page)
            redirect_count = self._count_redirects(response)
            content_type = response.headers.get("content-type", "") or ""
            html = "" if "html" not in content_type.lower() else (page.content() or "")

            internal, external = self._split_links(metadata["links"])

            return FetchResult(
                url=url,
                final_url=response.url or url,
                status_code=response.status,
                response_time_ms=elapsed,
                redirect_count=redirect_count,
                canonical_url=metadata["canonical"],
                content_type=content_type,
                html=html,
                title=metadata["title"],
                meta_description=metadata["meta"],
                h1=metadata["h1"],
                images_total=metadata["imagesTotal"],
                images_without_alt=metadata["imagesWithoutAlt"],
                is_indexable="noindex" not in (metadata["robots"] or "").lower(),
                internal_links=internal,
                external_links=external,
            )
        finally:
            page.close()

    # ------------------------------------------------------------------ #
    # internals
    # ------------------------------------------------------------------ #
    def _extract_metadata(self, page) -> dict:
        try:
            return page.evaluate(_PAGE_METADATA_JS) or {}
        except Exception as exc:  # noqa: BLE001
            log.warning("Metadata extraction failed: %s", exc)
            return {
                "links": [],
                "canonical": None,
                "robots": "",
                "title": "",
                "meta": "",
                "h1": "",
                "imagesTotal": 0,
                "imagesWithoutAlt": 0,
            }

    @staticmethod
    def _count_redirects(response) -> int:
        count = 0
        current = response.request
        while current is not None and getattr(current, "redirected_from", None):
            count += 1
            current = current.redirected_from
        return count

    def _split_links(self, links: list[str]) -> tuple[list[str], list[str]]:
        from .crawl import is_internal, normalize_url

        internal: list[str] = []
        external: list[str] = []
        for link in links:
            try:
                normalized = normalize_url(link)
            except ValueError:
                continue
            if is_internal(normalized, self.base_domain):
                internal.append(normalized)
            else:
                external.append(normalized)
        # dedupe, preserve order
        return _dedupe(internal), _dedupe(external)


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out
