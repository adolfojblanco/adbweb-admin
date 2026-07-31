"""
BFS URL frontier.

The crawler is a breadth-first walker over the URLs the fetcher
returns. It is independent of Playwright: the only thing it
needs is an object that implements ``fetch(url) -> FetchResult``,
which is trivial to fake in tests.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Callable, Iterable, Protocol
from urllib.parse import urljoin, urlparse, urlunparse

from .fetcher import FetchResult, Fetcher


class FetcherLike(Protocol):
    base_domain: str

    def fetch(self, url: str) -> FetchResult: ...


def normalize_url(url: str) -> str:
    """Lower-case scheme/host, drop the fragment.

    The crawler never wants to enqueue the same logical page under
    two different URLs (``/foo`` vs ``/foo#bar``), so fragments are
    always stripped.
    """
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"Unsupported URL scheme: {parsed.scheme!r}")
    return urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path,
        parsed.params,
        parsed.query,
        "",
    ))


def is_internal(url: str, base_domain: str) -> bool:
    """True if ``url`` belongs to ``base_domain``."""
    parsed = urlparse(url)
    return parsed.netloc.lower() == base_domain.lower()


def is_html(content_type: str) -> bool:
    return "html" in (content_type or "").lower()


@dataclass
class Crawler:
    """Walks a website one internal link at a time."""

    fetcher: FetcherLike
    max_pages: int = 50
    include_external: bool = False

    def crawl(self, start_url: str) -> list[FetchResult]:
        try:
            start = normalize_url(start_url)
        except ValueError:
            return []

        base_domain = self.fetcher.base_domain
        visited: set[str] = set()
        queue: deque[str] = deque([start])
        results: list[FetchResult] = []

        while queue and len(results) < self.max_pages:
            url = queue.popleft()
            if url in visited:
                continue
            visited.add(url)

            result = self.fetcher.fetch(url)
            results.append(result)

            if result.error or not is_html(result.content_type):
                continue

            for link in result.internal_links:
                if link not in visited:
                    queue.append(link)
            if self.include_external:
                for link in result.external_links:
                    if link not in visited:
                        queue.append(link)

        return results
