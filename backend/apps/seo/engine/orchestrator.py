"""
Audit engine orchestrator.

The orchestrator instantiates every registered analyzer, runs them
against the same :class:`AnalyzerContext` and aggregates the
results. Analyzers are run sequentially in registration order but
they are independent: a failure in one analyzer is captured in
its :class:`AnalyzerResult` and does not abort the audit.
"""
from __future__ import annotations

import logging
import time
import traceback
from typing import Sequence, Type

from ..models import SEOAudit
from .base import AnalyzerContext, BaseAnalyzer
from .registry import AnalyzerRegistry
from .results import AnalyzerResult, AuditResult

log = logging.getLogger(__name__)


class AuditEngine:
    """Runs every registered analyzer against one audit and aggregates."""

    def __init__(self, analyzers: Sequence[Type[BaseAnalyzer]] | None = None) -> None:
        self._analyzers: Sequence[Type[BaseAnalyzer]] = (
            list(analyzers) if analyzers is not None else list(AnalyzerRegistry.all())
        )

    @property
    def analyzers(self) -> Sequence[Type[BaseAnalyzer]]:
        return tuple(self._analyzers)

    def run(self, audit: SEOAudit) -> AuditResult:
        """Run the full pipeline for one audit."""
        context = AnalyzerContext(audit=audit)
        start = time.monotonic()
        results: list[AnalyzerResult] = []
        for analyzer_cls in self._analyzers:
            results.append(self._run_one(analyzer_cls, context))
        aggregated = self._aggregate(audit, results)
        aggregated.duration_ms = int((time.monotonic() - start) * 1000)
        return aggregated

    # ------------------------------------------------------------------ #
    # internals
    # ------------------------------------------------------------------ #
    def _run_one(
        self, analyzer_cls: Type[BaseAnalyzer], context: AnalyzerContext
    ) -> AnalyzerResult:
        """Run a single analyzer and capture failures in its result."""
        start = time.monotonic()
        name = getattr(analyzer_cls, "name", analyzer_cls.__name__)
        try:
            result = analyzer_cls().run(context)
        except Exception as exc:  # noqa: BLE001 - we want to swallow & surface
            log.exception("Analyzer %s failed", name)
            result = AnalyzerResult(
                analyzer=name,
                score=0,
                metadata={
                    "error": str(exc),
                    "traceback": traceback.format_exc(limit=4),
                },
            )
        result.analyzer = result.analyzer or name
        result.duration_ms = int((time.monotonic() - start) * 1000)
        return result

    def _aggregate(
        self, audit: SEOAudit, results: list[AnalyzerResult]
    ) -> AuditResult:
        """Aggregate per-analyzer results into one :class:`AuditResult`."""
        if not results:
            return AuditResult(audit_id=audit.id)

        breakdown: dict[str, int] = {r.analyzer: r.score for r in results}
        overall_score = round(sum(r.score for r in results) / len(results))
        total_errors = sum(len(r.errors) for r in results)
        total_warnings = sum(len(r.warnings) for r in results)
        total_recommendations = sum(len(r.recommendations) for r in results)

        return AuditResult(
            audit_id=audit.id,
            analyzer_results=results,
            overall_score=overall_score,
            total_errors=total_errors,
            total_warnings=total_warnings,
            total_recommendations=total_recommendations,
            breakdown=breakdown,
        )
