"""Unit tests for the crawler.

Playwright is mocked at the Fetcher boundary so the tests run
without a real browser or network.
"""
from __future__ import annotations

from unittest.mock import patch
from urllib.parse import urlparse

from django.test import SimpleTestCase, TestCase

from apps.seo.crawler import Crawler, FetchResult
from apps.seo.crawler.crawl import is_internal, normalize_url
from apps.seo.models import SEOAudit, SEOPage, Website
from apps.seo.services import crawl_audit, persist_crawl_results


# ---------------------------------------------------------------------- #
# URL helpers
# ---------------------------------------------------------------------- #
class NormalizeUrlTests(SimpleTestCase):
    def test_lowercases_host_and_scheme(self):
        self.assertEqual(
            normalize_url("HTTPS://Example.COM/Path"),
            "https://example.com/Path",
        )

    def test_drops_fragment(self):
        self.assertEqual(
            normalize_url("https://example.com/page#section"),
            "https://example.com/page",
        )

    def test_keeps_query(self):
        self.assertEqual(
            normalize_url("https://example.com/p?a=1&b=2"),
            "https://example.com/p?a=1&b=2",
        )

    def test_rejects_non_http(self):
        with self.assertRaises(ValueError):
            normalize_url("ftp://example.com/")
        with self.assertRaises(ValueError):
            normalize_url("javascript:void(0)")


class IsInternalTests(SimpleTestCase):
    def test_same_host(self):
        self.assertTrue(is_internal("https://example.com/x", "example.com"))

    def test_different_host(self):
        self.assertFalse(is_internal("https://other.com/x", "example.com"))

    def test_subdomain_is_external(self):
        # We treat the registered domain as the boundary; subdomains
        # are external on purpose to keep the BFS predictable.
        self.assertFalse(is_internal("https://blog.example.com/x", "example.com"))


# ---------------------------------------------------------------------- #
# Crawler algorithm with a fake fetcher
# ---------------------------------------------------------------------- #
class _FakeFetcher:
    """In-memory fetcher used to drive the Crawler deterministically."""

    def __init__(self, base_domain: str, pages: dict[str, FetchResult]):
        self.base_domain = base_domain
        self._pages = pages
        self.calls: list[str] = []

    def fetch(self, url: str) -> FetchResult:
        self.calls.append(url)
        return self._pages.get(url) or FetchResult(
            url=url,
            final_url=url,
            status_code=404,
            response_time_ms=1,
            redirect_count=0,
            canonical_url=None,
            content_type="text/html",
            html="",
        )


def _page(url, *, links=None, content_type="text/html", status=200, error=None):
    normalized_links = [normalize_url(l) for l in (links or [])]
    internal, external = [], []
    for link in normalized_links:
        if is_internal(link, urlparse(url).netloc):
            internal.append(link)
        else:
            external.append(link)
    return FetchResult(
        url=normalize_url(url),
        final_url=normalize_url(url),
        status_code=status,
        response_time_ms=10,
        redirect_count=0,
        canonical_url=None,
        content_type=content_type,
        html="<html></html>",
        internal_links=internal,
        external_links=external,
        error=error,
    )


class CrawlerBfsTests(SimpleTestCase):
    def test_visits_internal_links_bfs(self):
        start = "https://example.com/"
        a = "https://example.com/a"
        b = "https://example.com/b"
        c = "https://example.com/a/c"
        external = "https://other.com/x"

        pages = {
            normalize_url(start): _page(start, links=[a, b, external]),
            normalize_url(a): _page(a, links=[c]),
            normalize_url(b): _page(b, links=[]),
            normalize_url(c): _page(c, links=[]),
        }
        fetcher = _FakeFetcher("example.com", pages)
        crawler = Crawler(fetcher=fetcher, max_pages=10)

        results = crawler.crawl(start)
        urls = [r.url for r in results]
        self.assertEqual(urls, [start, a, b, c])
        self.assertNotIn(external, urls)

    def test_respects_max_pages(self):
        start = "https://example.com/"
        pages = {
            normalize_url(start): _page(start, links=[
                f"https://example.com/p{i}" for i in range(5)
            ]),
        }
        for i in range(5):
            url = f"https://example.com/p{i}"
            pages[normalize_url(url)] = _page(url, links=[])

        fetcher = _FakeFetcher("example.com", pages)
        crawler = Crawler(fetcher=fetcher, max_pages=3)
        results = crawler.crawl(start)
        self.assertEqual(len(results), 3)

    def test_does_not_visit_failed_pages(self):
        start = "https://example.com/"
        bad = "https://example.com/broken"
        pages = {
            normalize_url(start): _page(start, links=[bad]),
            normalize_url(bad): _page(
                bad, links=[], status=0, error="timeout"
            ),
        }
        fetcher = _FakeFetcher("example.com", pages)
        crawler = Crawler(fetcher=fetcher, max_pages=10)
        results = crawler.crawl(start)
        self.assertEqual({r.url for r in results}, {
            normalize_url(start), normalize_url(bad),
        })

    def test_does_not_revisit(self):
        start = "https://example.com/"
        a = "https://example.com/a"
        pages = {
            normalize_url(start): _page(start, links=[a, a, a]),
            normalize_url(a): _page(a, links=[start]),
        }
        fetcher = _FakeFetcher("example.com", pages)
        crawler = Crawler(fetcher=fetcher, max_pages=10)
        results = crawler.crawl(start)
        self.assertEqual(len(results), 2)
        self.assertEqual(fetcher.calls, [start, a])

    def test_skips_non_html_content(self):
        start = "https://example.com/"
        pdf = "https://example.com/file.pdf"
        pages = {
            normalize_url(start): _page(start, links=[pdf]),
            normalize_url(pdf): _page(pdf, links=[], content_type="application/pdf"),
        }
        fetcher = _FakeFetcher("example.com", pages)
        crawler = Crawler(fetcher=fetcher, max_pages=10)
        results = crawler.crawl(start)
        # The PDF is visited once (it's a page) but no new links
        # are enqueued from it.
        self.assertEqual(len(results), 2)
        self.assertEqual(len(fetcher.calls), 2)


# ---------------------------------------------------------------------- #
# Service persistence (no real Playwright)
# ---------------------------------------------------------------------- #
class PersistCrawlResultsTests(TestCase):
    def setUp(self):
        self.website = Website.objects.create(name="Demo", domain="demo.com")
        self.audit = SEOAudit.objects.create(
            website=self.website, target_url="https://demo.com/"
        )

    def test_upsert_creates_pages(self):
        results = [
            _page("https://demo.com/", links=["https://demo.com/a"]),
            _page("https://demo.com/a", links=[]),
        ]
        persist_crawl_results(self.audit, results)
        self.assertEqual(SEOPage.objects.filter(audit=self.audit).count(), 2)

    def test_upsert_is_idempotent(self):
        results = [_page("https://demo.com/", links=[])]
        persist_crawl_results(self.audit, results)
        persist_crawl_results(self.audit, results)
        self.assertEqual(SEOPage.objects.filter(audit=self.audit).count(), 1)

    def test_stores_observed_data(self):
        result = _page("https://demo.com/", links=["https://other.com/x"])
        result.status_code = 200
        result.response_time_ms = 432
        result.canonical_url = "https://demo.com/canonical"
        result.title = "Home"
        result.meta_description = "Home page"
        result.h1 = "Welcome"
        result.images_total = 3
        result.images_without_alt = 1
        result.is_indexable = False
        result.raw_html = "<html><body>hi</body></html>"

        persist_crawl_results(self.audit, [result])
        page = SEOPage.objects.get(audit=self.audit, url="https://demo.com/")
        self.assertEqual(page.status_code, 200)
        self.assertEqual(page.response_time_ms, 432)
        self.assertEqual(page.canonical_url, "https://demo.com/canonical")
        self.assertEqual(page.title, "Home")
        self.assertEqual(page.h1, "Welcome")
        self.assertEqual(page.images_total, 3)
        self.assertEqual(page.images_without_alt, 1)
        self.assertFalse(page.is_indexable)
        self.assertEqual(page.internal_links, 0)
        self.assertEqual(page.external_links, 1)
        self.assertEqual(page.raw_html, "<html><body>hi</body></html>")
        self.assertIsNotNone(page.crawled_at)


class CrawlAuditServiceTests(TestCase):
    """End-to-end of the service with the Fetcher patched out."""

    def setUp(self):
        self.website = Website.objects.create(name="Demo", domain="demo.com")
        self.audit = SEOAudit.objects.create(
            website=self.website,
            target_url="https://demo.com/",
            max_pages=5,
        )

    @patch("apps.seo.services.Fetcher")
    def test_crawl_audit_runs_end_to_end(self, MockFetcher):
        fake = _FakeFetcher("demo.com", {
            "https://demo.com/": _page("https://demo.com/", links=[]),
        })
        # Playwright's context-manager protocol is reproduced by
        # binding __enter__/__exit__ to the fake itself.
        fake.__enter__ = lambda self=fake: self
        fake.__exit__ = lambda *args, **kwargs: None
        MockFetcher.return_value = fake

        crawl_audit(self.audit.id)

        self.audit.refresh_from_db()
        self.assertEqual(self.audit.status, SEOAudit.Status.CRAWLED)
        self.assertEqual(self.audit.pages_crawled, 1)
        self.assertIsNotNone(self.audit.started_at)
        self.assertIsNotNone(self.audit.completed_at)
        self.assertEqual(SEOPage.objects.filter(audit=self.audit).count(), 1)

    @patch("apps.seo.services.Fetcher")
    def test_crawl_audit_marks_failed_on_crash(self, MockFetcher):
        MockFetcher.side_effect = RuntimeError("playwright is not installed")

        with self.assertRaises(RuntimeError):
            crawl_audit(self.audit.id)

        self.audit.refresh_from_db()
        self.assertEqual(self.audit.status, SEOAudit.Status.FAILED)
