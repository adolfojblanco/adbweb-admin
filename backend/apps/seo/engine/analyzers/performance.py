"""Performance analyzer.

Evaluates response time, payload weight and image footprint of
each page. Independent of every other analyzer.
"""
from __future__ import annotations

from ..base import AnalyzerContext
from ..registry import AnalyzerRegistry
from ..results import AnalyzerResult, Finding, Recommendation
from ._helpers import score_from_findings


@AnalyzerRegistry.register
class PerformanceAnalyzer:
    name = "performance"
    category = "PERFORMANCE"

    SLOW_RESPONSE_MS = 1500
    VERY_SLOW_RESPONSE_MS = 3000
    HEAVY_PAGE_KB = 500
    IMAGE_HEAVY_THRESHOLD = 30

    def run(self, context: AnalyzerContext) -> AnalyzerResult:
        result = AnalyzerResult(analyzer=self.name)
        for page in context.pages:
            self._check_response_time(page, result)
            self._check_payload(page, result)
            self._check_image_weight(page, result)

        result.score = score_from_findings(result.errors, result.warnings)
        if result.errors or result.warnings:
            result.recommendations.append(
                Recommendation.make(
                    code="PERF_TUNE",
                    title="Mejora los tiempos de respuesta y el peso de las páginas",
                    description=(
                        "Reduce el tiempo de respuesta, el tamaño de las "
                        "páginas y el número de imágenes sin texto "
                        "alternativo para mejorar Core Web Vitals."
                    ),
                    priority="MEDIUM",
                )
            )
        return result

    # ------------------------------------------------------------------ #
    def _check_response_time(self, page, result: AnalyzerResult) -> None:
        if page.response_time_ms >= self.VERY_SLOW_RESPONSE_MS:
            result.errors.append(
                Finding.make(
                    code="PERF_VERY_SLOW",
                    message=(
                        f"{page.url} tarda {page.response_time_ms} ms en "
                        f"responder."
                    ),
                    severity="ERROR",
                    category=self.category,
                    page=page,
                )
            )
        elif page.response_time_ms >= self.SLOW_RESPONSE_MS:
            result.warnings.append(
                Finding.make(
                    code="PERF_SLOW",
                    message=(
                        f"{page.url} tarda {page.response_time_ms} ms en "
                        f"responder."
                    ),
                    severity="WARNING",
                    category=self.category,
                    page=page,
                )
            )

    def _check_payload(self, page, result: AnalyzerResult) -> None:
        if page.content_length >= self.HEAVY_PAGE_KB * 1024:
            result.warnings.append(
                Finding.make(
                    code="PERF_HEAVY_PAGE",
                    message=(
                        f"{page.url} pesa {page.content_length // 1024} KB."
                    ),
                    severity="WARNING",
                    category=self.category,
                    page=page,
                )
            )

    def _check_image_weight(self, page, result: AnalyzerResult) -> None:
        if page.images_total >= self.IMAGE_HEAVY_THRESHOLD:
            result.warnings.append(
                Finding.make(
                    code="PERF_TOO_MANY_IMAGES",
                    message=(
                        f"{page.url} contiene {page.images_total} imágenes."
                    ),
                    severity="WARNING",
                    category=self.category,
                    page=page,
                )
            )
