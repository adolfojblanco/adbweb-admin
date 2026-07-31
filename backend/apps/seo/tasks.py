"""
Celery tasks for the SEO module.

The view layer never calls the engine or the crawler directly: it
always hands the audit over to one of the tasks defined here,
which are the only entry points that run the pipelines outside
of tests.
"""
from __future__ import annotations

import logging
from uuid import UUID

from celery import shared_task

log = logging.getLogger(__name__)


@shared_task(name="apps.seo.run_audit")
def run_audit_task(audit_id: str) -> dict:
    """Run the analyzer pipeline for an audit.

    Returns a small dict so the task result is JSON-serializable
    and visible in Celery's result backend.
    """
    from .services import run_audit

    result = run_audit(UUID(audit_id))
    return {
        "audit_id": str(result.audit_id),
        "overall_score": result.overall_score,
        "total_errors": result.total_errors,
        "total_warnings": result.total_warnings,
        "total_recommendations": result.total_recommendations,
        "duration_ms": result.duration_ms,
    }


@shared_task(name="apps.seo.crawl_audit", bind=True, max_retries=0)
def crawl_audit_task(self, audit_id: str) -> dict:
    """Crawl the website of an audit and persist every visited page.

    The task does NOT run the analyzer pipeline. The audit will
    transition to ``CRAWLED`` and a subsequent ``run_audit_task``
    invocation is responsible for the analysis step.
    """
    from .services import crawl_audit

    log.info("Crawling audit %s", audit_id)
    results = crawl_audit(UUID(audit_id))
    return {
        "audit_id": audit_id,
        "pages_crawled": len(results),
    }


@shared_task(name="apps.seo.run_lighthouse", bind=True, max_retries=0)
def run_lighthouse_task(self, page_id: str) -> dict:
    """Run Lighthouse against a single crawled page and persist metrics."""
    from .services import run_lighthouse_for_page

    log.info("Running Lighthouse for page %s", page_id)
    result = run_lighthouse_for_page(UUID(page_id))
    return {
        "page_id": page_id,
        "lighthouse_id": str(result.id),
        "performance": result.performance_score,
        "accessibility": result.accessibility_score,
        "seo": result.seo_score,
        "best_practices": result.best_practices_score,
        "error": result.error_message or None,
    }
