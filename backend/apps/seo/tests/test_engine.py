"""Tests for the audit engine, its analyzers and their independence."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase

from apps.seo.engine import (
    AnalyzerContext,
    AnalyzerRegistry,
    AuditEngine,
)
from apps.seo.engine.analyzers import (
    AccessibilityAnalyzer,
    AIRecommendationEngine,
    OnPageAnalyzer,
    PerformanceAnalyzer,
    TechnicalAnalyzer,
)
from apps.seo.engine.results import AnalyzerResult, Finding
from apps.seo.models import (
    SEOAudit,
    SEOIssue,
    SEOPage,
    SEORecommendation,
    SEOScore,
    Website,
)


# ---------------------------------------------------------------------- #
# Helpers
# ---------------------------------------------------------------------- #
def _page(**overrides) -> SimpleNamespace:
    base = dict(
        id=None,
        url="https://example.com/",
        status_code=200,
        title="Sample page title that fits the limits OK",
        meta_description="A reasonably long meta description for the page so it does not trigger the warning threshold.",
        h1="A heading",
        content_type="text/html",
        content_length=10_000,
        response_time_ms=200,
        internal_links=3,
        external_links=1,
        images_total=2,
        images_without_alt=0,
        is_indexable=True,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def _audit_with_pages(pages: list) -> SEOAudit:
    """Build an in-memory SEOAudit with ``pages`` attached."""
    audit = SEOAudit(target_url="https://example.com/")
    audit.pages = SimpleNamespace(all=lambda: pages)
    return audit


# ---------------------------------------------------------------------- #
# Analyzers in isolation
# ---------------------------------------------------------------------- #
class TechnicalAnalyzerTests(SimpleTestCase):
    def setUp(self):
        self.analyzer = TechnicalAnalyzer()

    def test_clean_page_scores_full(self):
        ctx = AnalyzerContext(audit=_audit_with_pages([_page()]))
        result = self.analyzer.run(ctx)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])
        self.assertEqual(result.score, 100)

    def test_https_error(self):
        ctx = AnalyzerContext(
            audit=_audit_with_pages([_page(url="http://example.com/")])
        )
        result = self.analyzer.run(ctx)
        self.assertTrue(any(f.code == "TECH_NOT_HTTPS" for f in result.errors))

    def test_5xx_is_critical(self):
        ctx = AnalyzerContext(
            audit=_audit_with_pages([_page(status_code=503)])
        )
        result = self.analyzer.run(ctx)
        self.assertEqual(result.errors[0].severity, "CRITICAL")


class OnPageAnalyzerTests(SimpleTestCase):
    def setUp(self):
        self.analyzer = OnPageAnalyzer()

    def test_missing_title_is_error(self):
        ctx = AnalyzerContext(audit=_audit_with_pages([_page(title="")]))
        result = self.analyzer.run(ctx)
        self.assertTrue(any(f.code == "ONPAGE_NO_TITLE" for f in result.errors))

    def test_short_title_is_warning(self):
        ctx = AnalyzerContext(audit=_audit_with_pages([_page(title="Hi")]))
        result = self.analyzer.run(ctx)
        self.assertTrue(any(f.code == "ONPAGE_SHORT_TITLE" for f in result.warnings))


class PerformanceAnalyzerTests(SimpleTestCase):
    def setUp(self):
        self.analyzer = PerformanceAnalyzer()

    def test_very_slow_response(self):
        ctx = AnalyzerContext(audit=_audit_with_pages([_page(response_time_ms=5000)]))
        result = self.analyzer.run(ctx)
        self.assertTrue(any(f.code == "PERF_VERY_SLOW" for f in result.errors))


class AccessibilityAnalyzerTests(SimpleTestCase):
    def setUp(self):
        self.analyzer = AccessibilityAnalyzer()

    def test_many_images_without_alt(self):
        ctx = AnalyzerContext(audit=_audit_with_pages([_page(images_without_alt=10)]))
        result = self.analyzer.run(ctx)
        self.assertTrue(any(f.code == "A11Y_IMG_NO_ALT" for f in result.errors))


class AIRecommendationEngineTests(SimpleTestCase):
    def setUp(self):
        self.analyzer = AIRecommendationEngine()

    def test_emits_recommendations_for_missing_title(self):
        ctx = AnalyzerContext(audit=_audit_with_pages([_page(title="")]))
        result = self.analyzer.run(ctx)
        self.assertTrue(
            any(r.code == "ADD_TITLE" for r in result.recommendations)
        )


# ---------------------------------------------------------------------- #
# Independence
# ---------------------------------------------------------------------- #
class AnalyzerIndependenceTests(SimpleTestCase):
    """Analyzers must not consult each other."""

    def test_analyzers_do_not_import_each_other(self):
        from apps.seo.engine.analyzers import (
            accessibility,
            ai_recommendation,
            onpage,
            performance,
            technical,
        )

        for mod in (accessibility, ai_recommendation, onpage, performance, technical):
            other_names = {
                "AccessibilityAnalyzer",
                "AIRecommendationEngine",
                "OnPageAnalyzer",
                "PerformanceAnalyzer",
                "TechnicalAnalyzer",
            } - {cls for cls in mod.__dict__.values() if isinstance(cls, type)}
            for name in other_names:
                self.assertNotIn(
                    name, mod.__dict__,
                    f"{mod.__name__} references sibling analyzer {name}",
                )

    def test_running_subset_does_not_affect_others(self):
        registry_before = list(AnalyzerRegistry.all())
        try:
            AnalyzerRegistry.clear()
            AnalyzerRegistry.register(TechnicalAnalyzer)
            AnalyzerRegistry.register(OnPageAnalyzer)
            audit = _audit_with_pages([_page()])

            full = AuditEngine([TechnicalAnalyzer, OnPageAnalyzer]).run(audit)
            only_tech = AuditEngine([TechnicalAnalyzer]).run(audit)

            tech_result = next(r for r in full.analyzer_results if r.analyzer == "technical")
            only_tech_result = only_tech.analyzer_results[0]
            self.assertEqual(tech_result.score, only_tech_result.score)
            self.assertEqual(len(tech_result.errors), len(only_tech_result.errors))
        finally:
            AnalyzerRegistry.clear()
            for cls in registry_before:
                AnalyzerRegistry.register(cls)


# ---------------------------------------------------------------------- #
# Orchestrator
# ---------------------------------------------------------------------- #
class AuditEngineTests(SimpleTestCase):
    def setUp(self):
        AnalyzerRegistry.clear()
        AnalyzerRegistry.register(TechnicalAnalyzer)
        AnalyzerRegistry.register(OnPageAnalyzer)
        AnalyzerRegistry.register(PerformanceAnalyzer)
        AnalyzerRegistry.register(AccessibilityAnalyzer)
        AnalyzerRegistry.register(AIRecommendationEngine)

    def tearDown(self):
        AnalyzerRegistry.clear()

    def test_engine_runs_every_registered_analyzer(self):
        engine = AuditEngine()
        ctx_audit = _audit_with_pages([_page()])
        result = engine.run(ctx_audit)
        names = {r.analyzer for r in result.analyzer_results}
        self.assertEqual(
            names,
            {"technical", "onpage", "performance", "accessibility", "ai_recommendation"},
        )

    def test_engine_aggregates_scores(self):
        engine = AuditEngine()
        result = engine.run(_audit_with_pages([_page()]))
        self.assertEqual(
            result.overall_score,
            round(sum(r.score for r in result.analyzer_results) / len(result.analyzer_results)),
        )
        self.assertEqual(
            result.breakdown,
            {r.analyzer: r.score for r in result.analyzer_results},
        )

    def test_engine_swallows_analyzer_exceptions(self):
        class BoomAnalyzer:
            name = "boom"
            category = "META"

            def run(self, context):
                raise RuntimeError("kaboom")

        engine = AuditEngine([BoomAnalyzer])
        result = engine.run(_audit_with_pages([_page()]))
        boom = result.analyzer_results[0]
        self.assertEqual(boom.score, 0)
        self.assertIn("kaboom", boom.metadata["error"])


# ---------------------------------------------------------------------- #
# End-to-end persistence through services
# ---------------------------------------------------------------------- #
class RunAuditServiceTests(TestCase):
    def setUp(self):
        self.website = Website.objects.create(name="Demo", domain="demo.com")
        self.audit = SEOAudit.objects.create(
            website=self.website,
            target_url="https://demo.com/",
            max_pages=10,
        )
        SEOPage.objects.create(
            audit=self.audit,
            url="https://demo.com/",
            status_code=200,
            title="A page",
            meta_description="A meta",
            h1="Heading",
        )
        SEOPage.objects.create(
            audit=self.audit,
            url="http://demo.com/insecure",
            status_code=200,
            title="",
            meta_description="",
            h1="",
            images_without_alt=6,
        )

    def test_run_audit_persists_everything(self):
        from apps.seo.services import run_audit

        result = run_audit(self.audit.id)

        self.audit.refresh_from_db()
        self.assertEqual(self.audit.status, SEOAudit.Status.COMPLETED)
        self.assertGreater(self.audit.issues_count, 0)
        self.assertGreater(self.audit.pages_crawled, 0)
        self.assertIsNotNone(self.audit.started_at)
        self.assertIsNotNone(self.audit.completed_at)

        self.assertTrue(SEOIssue.objects.filter(audit=self.audit).exists())
        self.assertTrue(SEORecommendation.objects.filter(page__audit=self.audit).exists())

        score = SEOScore.objects.get(audit=self.audit)
        self.assertEqual(score.value, result.overall_score)
        self.assertEqual(set(score.breakdown), {
            "technical", "onpage", "performance", "accessibility", "ai_recommendation",
        })

    def test_run_audit_is_idempotent(self):
        from apps.seo.services import run_audit

        run_audit(self.audit.id)
        first_count = SEOIssue.objects.filter(audit=self.audit).count()

        run_audit(self.audit.id)
        second_count = SEOIssue.objects.filter(audit=self.audit).count()
        self.assertEqual(first_count, second_count)
