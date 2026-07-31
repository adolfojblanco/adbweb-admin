"""
SEO module write-side services.

Views and Celery tasks call into this module exclusively. No
business logic lives outside this file (or, in special cases,
under :mod:`apps.seo.selectors` for read-side queries and under
:mod:`apps.seo.engine` for the actual analyzers).

Public API
----------

* :func:`create_audit`      – create a pending audit for a website.
* :func:`enqueue_audit`     – hand an audit off to Celery (analyzer).
* :func:`run_audit`         – run the engine synchronously and persist
                              findings, recommendations and score.
* :func:`cancel_audit`      – mark an audit as cancelled.
* :func:`enqueue_crawl`     – hand an audit off to Celery (crawler).
* :func:`crawl_audit`       – run the crawler synchronously and persist
                              every page it visited.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from django.db import transaction

from .crawler import Crawler, CrawlerSettings, Fetcher, FetchResult
from .engine import AuditEngine, AuditResult
from .engine.analyzers import (  # noqa: F401 - import for side effects
    AccessibilityAnalyzer,
    AIRecommendationEngine,
    OnPageAnalyzer,
    PerformanceAnalyzer,
    TechnicalAnalyzer,
)
from .engine.results import AnalyzerResult, Finding, Recommendation
from .lighthouse import (
    LighthouseNotInstalled,
    LighthouseReport,
    run_lighthouse,
)
from .models import (
    LighthouseResult,
    SEOAudit,
    SEOIssue,
    SEOPage,
    SEORecommendation,
    SEOScore,
)

log = logging.getLogger(__name__)

__all__ = [
    "create_audit",
    "enqueue_audit",
    "run_audit",
    "cancel_audit",
    "enqueue_crawl",
    "crawl_audit",
    "enqueue_lighthouse",
    "run_lighthouse_for_page",
]


# ---------------------------------------------------------------------- #
# write-side use cases
# ---------------------------------------------------------------------- #
def create_audit(*, website_id: UUID, target_url: str, max_pages: int = 50) -> SEOAudit:
    """Create a pending audit for a website."""
    return SEOAudit.objects.create(
        website_id=website_id,
        target_url=target_url,
        max_pages=max_pages,
        status=SEOAudit.Status.PENDING,
    )


def enqueue_audit(audit_id: UUID) -> None:
    """Hand an audit off to the Celery worker."""
    # Local import to avoid pulling Celery into management commands
    # that don't need it.
    from .tasks import run_audit_task

    run_audit_task.delay(str(audit_id))


def cancel_audit(audit_id: UUID) -> SEOAudit:
    audit = SEOAudit.objects.get(pk=audit_id)
    if audit.status in {SEOAudit.Status.COMPLETED, SEOAudit.Status.CANCELLED}:
        return audit
    audit.status = SEOAudit.Status.CANCELLED
    audit.completed_at = _now()
    audit.save(update_fields=["status", "completed_at", "updated_at"])
    return audit


@transaction.atomic
def run_audit(audit_id: UUID) -> AuditResult:
    """Run the full pipeline synchronously and persist its output.

    This is the only entry point the engine exposes. It owns the
    audit lifecycle (PENDING -> RUNNING -> COMPLETED / FAILED) and
    is the single place that turns analyzer results into rows in
    the database.
    """
    audit = (
        SEOAudit.objects
        .select_for_update()
        .get(pk=audit_id)
    )
    _mark_running(audit)
    engine = AuditEngine()
    try:
        result = engine.run(audit)
    except Exception:
        log.exception("Audit %s failed", audit_id)
        _mark_failed(audit)
        raise

    persist_audit_result(audit, result)
    _mark_completed(audit, result)
    return result


def persist_audit_result(audit: SEOAudit, result: AuditResult) -> None:
    """Turn an :class:`AuditResult` into rows.

    The previous findings and recommendations of the audit are
    wiped first so re-running an audit yields a clean snapshot.
    """
    SEOIssue.objects.filter(audit=audit).delete()
    SEORecommendation.objects.filter(page__audit=audit).delete()

    issues = _build_issues(audit, result)
    recommendations = _build_recommendations(audit, result)
    if issues:
        SEOIssue.objects.bulk_create(issues, batch_size=500)
    if recommendations:
        SEORecommendation.objects.bulk_create(recommendations, batch_size=500)

    SEOScore.objects.update_or_create(
        audit=audit,
        defaults={
            "value": result.overall_score,
            "breakdown": result.breakdown,
        },
    )

    audit.issues_count = SEOIssue.objects.filter(audit=audit).count()
    audit.save(update_fields=["issues_count", "updated_at"])


# ---------------------------------------------------------------------- #
# internal helpers
# ---------------------------------------------------------------------- #
def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _mark_running(audit: SEOAudit) -> None:
    audit.status = SEOAudit.Status.RUNNING
    audit.started_at = _now()
    audit.error_message = ""
    audit.save(update_fields=["status", "started_at", "error_message", "updated_at"])


def _mark_failed(audit: SEOAudit) -> None:
    audit.status = SEOAudit.Status.FAILED
    audit.completed_at = _now()
    audit.error_message = "Engine crashed; see server logs."
    audit.save(update_fields=["status", "completed_at", "error_message", "updated_at"])


def _mark_completed(audit: SEOAudit, result: AuditResult) -> None:
    audit.status = SEOAudit.Status.COMPLETED
    audit.completed_at = _now()
    if audit.started_at:
        delta = audit.completed_at - audit.started_at
        audit.duration_seconds = int(delta.total_seconds())
    audit.pages_crawled = audit.pages.count()
    audit.issues_count = result.total_errors + result.total_warnings
    audit.save(update_fields=[
        "status",
        "completed_at",
        "duration_seconds",
        "pages_crawled",
        "issues_count",
        "updated_at",
    ])


def _build_issues(
    audit: SEOAudit, result: AuditResult
) -> list[SEOIssue]:
    issues: list[SEOIssue] = []
    for analyzer_result in result.analyzer_results:
        for finding in analyzer_result.errors + analyzer_result.warnings:
            issues.append(_issue_from_finding(audit, finding))
    return issues


def _issue_from_finding(audit: SEOAudit, finding: Finding) -> SEOIssue:
    severity = finding.severity
    if severity == "CRITICAL":
        severity = SEOIssue.Severity.CRITICAL
    elif severity == "ERROR":
        severity = SEOIssue.Severity.ERROR
    elif severity == "WARNING":
        severity = SEOIssue.Severity.WARNING
    else:
        severity = SEOIssue.Severity.INFO

    category = finding.category
    valid_categories = {choice for choice, _ in SEOIssue.Category.choices}
    if category not in valid_categories:
        category = SEOIssue.Category.META

    return SEOIssue(
        audit=audit,
        page_id=finding.page_id,
        severity=severity,
        category=category,
        code=finding.code,
        message=finding.message,
    )


def _build_recommendations(
    audit: SEOAudit, result: AuditResult
) -> list[SEORecommendation]:
    recommendations: list[SEORecommendation] = []
    for analyzer_result in result.analyzer_results:
        for rec in analyzer_result.recommendations:
            recommendations.append(_recommendation_from_obj(audit, rec))
    return recommendations


def _recommendation_from_obj(
    audit: SEOAudit, rec: Recommendation
) -> SEORecommendation:
    priority = rec.priority
    valid = {choice for choice, _ in SEORecommendation.Priority.choices}
    if priority not in valid:
        priority = SEORecommendation.Priority.MEDIUM

    return SEORecommendation(
        page_id=rec.page_id,
        code=rec.code,
        title=rec.title,
        description=rec.description,
        priority=priority,
    )


# ---------------------------------------------------------------------- #
# crawler use cases
# ---------------------------------------------------------------------- #
def enqueue_crawl(audit_id: UUID) -> None:
    """Hand an audit over to the Celery crawler worker."""
    from .tasks import crawl_audit_task

    crawl_audit_task.delay(str(audit_id))


@transaction.atomic
def crawl_audit(audit_id: UUID) -> list[FetchResult]:
    """Crawl the website for ``audit`` and persist every visited page.

    The audit transitions ``PENDING -> RUNNING -> CRAWLED``. It does
    not run the analyzer pipeline; that is :func:`run_audit`'s job.
    """
    audit = (
        SEOAudit.objects
        .select_for_update()
        .select_related("website")
        .get(pk=audit_id)
    )
    _mark_crawling(audit)

    settings = CrawlerSettings.from_audit(audit)
    try:
        with Fetcher(
            base_domain=audit.website.domain,
            timeout_ms=settings.timeout_ms,
            headless=settings.headless,
            user_agent=settings.user_agent,
        ) as fetcher:
            crawler = Crawler(fetcher=fetcher, max_pages=settings.max_pages)
            results = crawler.crawl(audit.target_url)
    except Exception:
        log.exception("Crawl of audit %s crashed", audit_id)
        _mark_failed(audit)
        raise

    persist_crawl_results(audit, results)
    _mark_crawled(audit, results)
    return results


def persist_crawl_results(
    audit: SEOAudit, results: list[FetchResult]
) -> list[SEOPage]:
    """Upsert a :class:`FetchResult` for every URL the crawler visited.

    Pages are matched by ``(audit, url)``; running a crawl a second
    time overwrites the previous data without producing duplicates.
    """
    pages: list[SEOPage] = []
    for result in results:
        page, _ = SEOPage.objects.update_or_create(
            audit=audit,
            url=result.url,
            defaults=_page_defaults(result),
        )
        pages.append(page)
    return pages


# ---------------------------------------------------------------------- #
# crawler helpers
# ---------------------------------------------------------------------- #
def _mark_crawling(audit: SEOAudit) -> None:
    audit.status = SEOAudit.Status.RUNNING
    audit.started_at = _now()
    audit.error_message = ""
    audit.save(update_fields=[
        "status", "started_at", "error_message", "updated_at",
    ])


def _mark_crawled(audit: SEOAudit, results: list[FetchResult]) -> None:
    audit.status = SEOAudit.Status.CRAWLED
    audit.completed_at = _now()
    audit.pages_crawled = len(results)
    if audit.started_at:
        delta = audit.completed_at - audit.started_at
        audit.duration_seconds = int(delta.total_seconds())
    audit.save(update_fields=[
        "status",
        "completed_at",
        "pages_crawled",
        "duration_seconds",
        "updated_at",
    ])


def _page_defaults(result: FetchResult) -> dict:
    return {
        "status_code": result.status_code,
        "title": result.title,
        "meta_description": result.meta_description,
        "h1": result.h1,
        "content_type": result.content_type,
        "content_length": len(result.html.encode("utf-8")) if result.html else 0,
        "response_time_ms": result.response_time_ms,
        "internal_links": len(result.internal_links),
        "external_links": len(result.external_links),
        "images_total": result.images_total,
        "images_without_alt": result.images_without_alt,
        "is_indexable": result.is_indexable,
        "canonical_url": result.canonical_url or None,
        "redirect_count": result.redirect_count,
        "raw_html": result.html,
        "crawled_at": _now(),
    }


# ---------------------------------------------------------------------- #
# lighthouse use cases
# ---------------------------------------------------------------------- #
def enqueue_lighthouse(page_id: UUID) -> None:
    """Hand a single page off to the Celery Lighthouse worker."""
    from .tasks import run_lighthouse_task

    run_lighthouse_task.delay(str(page_id))


def run_lighthouse_for_page(page_id: UUID) -> LighthouseResult:
    """Run Lighthouse for one page and persist the metrics.

    One ``LighthouseResult`` row is created per (page, run). The
    latest run is exposed through the reverse manager on
    ``SEOPage.lighthouse_results``.
    """
    page = SEOPage.objects.select_related("audit__website").get(pk=page_id)

    try:
        report = run_lighthouse(page.url)
    except LighthouseNotInstalled as exc:
        report = _error_report(page.url, str(exc))

    return persist_lighthouse_report(page, report)


def persist_lighthouse_report(
    page: SEOPage, report: LighthouseReport
) -> LighthouseResult:
    """Turn a :class:`LighthouseReport` into a row."""
    return LighthouseResult.objects.create(
        page=page,
        performance_score=report.performance,
        accessibility_score=report.accessibility,
        seo_score=report.seo,
        best_practices_score=report.best_practices,
        cls=report.cls,
        lcp=report.lcp,
        inp=report.inp,
        fcp=report.fcp,
        ttfb=report.ttfb,
        speed_index=report.speed_index,
        lighthouse_version=report.lighthouse_version,
        user_agent=report.user_agent,
        error_message=report.error or "",
    )


def _error_report(url: str, error: str) -> LighthouseReport:
    return LighthouseReport(
        url=url,
        final_url=url,
        lighthouse_version="",
        user_agent="",
        performance=None,
        accessibility=None,
        seo=None,
        best_practices=None,
        cls=None,
        lcp=None,
        inp=None,
        fcp=None,
        ttfb=None,
        speed_index=None,
        error=error,
    )
