"""Technical SEO analyzer.

Focuses on HTTP-level concerns: status codes, transport security,
and crawlable infrastructure. The analyzer is independent: it
queries the pages of the audit and returns its own findings, score
and recommendations without consulting any other analyzer.
"""
from __future__ import annotations

from ..base import AnalyzerContext
from ..registry import AnalyzerRegistry
from ..results import AnalyzerResult, Finding, Recommendation
from ._helpers import score_from_findings


@AnalyzerRegistry.register
class TechnicalAnalyzer:
    name = "technical"
    category = "STATUS"

    SUCCESS_CODES = {200, 201, 204, 301, 302, 304, 307, 308}

    def run(self, context: AnalyzerContext) -> AnalyzerResult:
        result = AnalyzerResult(analyzer=self.name)
        pages = list(context.pages)

        for page in pages:
            self._check_status_code(page, result)
            self._check_https(page, result)
            self._check_indexable(page, result)

        result.score = score_from_findings(result.errors, result.warnings)
        if result.errors or result.warnings:
            result.recommendations.append(
                Recommendation.make(
                    code="TECH_HEALTH",
                    title="Revisa la salud técnica del sitio",
                    description=(
                        "Se detectaron problemas de estado HTTP, HTTPS o "
                        "directivas de indexabilidad. Resuélvelos antes de "
                        "optimizar el contenido."
                    ),
                    priority="HIGH" if result.errors else "MEDIUM",
                )
            )
        return result

    # ------------------------------------------------------------------ #
    def _check_status_code(self, page, result: AnalyzerResult) -> None:
        if not page.status_code:
            result.errors.append(
                Finding.make(
                    code="TECH_NO_STATUS",
                    message=f"La página {page.url} no devolvió código de estado.",
                    severity="ERROR",
                    category=self.category,
                    page=page,
                )
            )
            return
        if page.status_code >= 500:
            result.errors.append(
                Finding.make(
                    code="TECH_5XX",
                    message=f"Error de servidor ({page.status_code}) en {page.url}.",
                    severity="CRITICAL",
                    category=self.category,
                    page=page,
                )
            )
        elif page.status_code >= 400:
            result.errors.append(
                Finding.make(
                    code="TECH_4XX",
                    message=f"Error de cliente ({page.status_code}) en {page.url}.",
                    severity="ERROR",
                    category=self.category,
                    page=page,
                )
            )
        elif page.status_code not in self.SUCCESS_CODES:
            result.warnings.append(
                Finding.make(
                    code="TECH_UNUSUAL_STATUS",
                    message=f"Código de estado inusual ({page.status_code}) en {page.url}.",
                    severity="WARNING",
                    category=self.category,
                    page=page,
                )
            )

    def _check_https(self, page, result: AnalyzerResult) -> None:
        if page.url.startswith("http://"):
            result.errors.append(
                Finding.make(
                    code="TECH_NOT_HTTPS",
                    message=f"La página {page.url} no se sirve por HTTPS.",
                    severity="ERROR",
                    category=self.category,
                    page=page,
                )
            )

    def _check_indexable(self, page, result: AnalyzerResult) -> None:
        if not page.is_indexable:
            result.warnings.append(
                Finding.make(
                    code="TECH_NOINDEX",
                    message=f"La página {page.url} está marcada como no indexable.",
                    severity="WARNING",
                    category=self.category,
                    page=page,
                )
            )
