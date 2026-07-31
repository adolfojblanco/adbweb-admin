"""
Result types produced by the SEO audit engine.

* :class:`Finding`         – a single issue found on a page.
* :class:`Recommendation`  – an actionable fix proposed for a page.
* :class:`AnalyzerResult`  – the output of one analyzer.
* :class:`AuditResult`     – the aggregated output of the whole engine.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass
class Finding:
    """A single finding produced by an analyzer.

    The orchestrator is responsible for converting :class:`Finding`
    instances into :class:`apps.seo.models.SEOIssue` rows. The
    dataclass stays ORM-agnostic so analyzers can be unit-tested
    in isolation.
    """

    code: str
    message: str
    severity: str  # ERROR | CRITICAL | WARNING
    category: str
    page_id: UUID | None = None
    page_url: str = ""

    @classmethod
    def make(
        cls,
        *,
        code: str,
        message: str,
        severity: str,
        category: str,
        page=None,
    ) -> "Finding":
        return cls(
            code=code,
            message=message,
            severity=severity,
            category=category,
            page_id=getattr(page, "id", None) if page is not None else None,
            page_url=getattr(page, "url", "") or "",
        )


@dataclass
class Recommendation:
    """An actionable recommendation emitted by an analyzer."""

    code: str
    title: str
    description: str
    priority: str  # LOW | MEDIUM | HIGH | CRITICAL
    page_id: UUID | None = None
    page_url: str = ""

    @classmethod
    def make(
        cls,
        *,
        code: str,
        title: str,
        description: str,
        priority: str,
        page=None,
    ) -> "Recommendation":
        return cls(
            code=code,
            title=title,
            description=description,
            priority=priority,
            page_id=getattr(page, "id", None) if page is not None else None,
            page_url=getattr(page, "url", "") or "",
        )


@dataclass
class AnalyzerResult:
    """The output of a single analyzer.

    Analyzers MUST return exactly this shape. They are independent
    of each other: each one builds its own list of errors and
    warnings, computes its own score and proposes its own
    recommendations without looking at peer results.
    """

    analyzer: str
    errors: list[Finding] = field(default_factory=list)
    warnings: list[Finding] = field(default_factory=list)
    score: int = 100
    recommendations: list[Recommendation] = field(default_factory=list)
    duration_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditResult:
    """The aggregated output of the engine for one audit run."""

    audit_id: UUID
    analyzer_results: list[AnalyzerResult] = field(default_factory=list)
    overall_score: int = 0
    total_errors: int = 0
    total_warnings: int = 0
    total_recommendations: int = 0
    breakdown: dict[str, int] = field(default_factory=dict)
    duration_ms: int = 0
