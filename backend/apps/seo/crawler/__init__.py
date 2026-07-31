"""
Website crawler for the SEO module.

The crawler is intentionally split into two layers:

* :class:`Fetcher` – wraps a Playwright browser context and turns
  one URL into a :class:`FetchResult` (status, redirects, canonical,
  links, raw HTML, basic meta).
* :class:`Crawler` – implements the BFS frontier over the URLs
  returned by the fetcher, respecting a ``max_pages`` budget and
  the website domain.

The analyzer pipeline lives in :mod:`apps.seo.engine` and runs
*after* the crawl. The crawler itself does not analyze anything:
it just visits pages and records what it found.
"""
from .crawl import Crawler, is_internal, normalize_url
from .fetcher import Fetcher, FetchResult
from .settings import CrawlerSettings

__all__ = [
    "Crawler",
    "CrawlerSettings",
    "Fetcher",
    "FetchResult",
    "is_internal",
    "normalize_url",
]
