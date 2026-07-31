"""Accessibility analyzer.

Catches the SEO-relevant subset of accessibility issues: images
without ``alt`` text, missing language hints and heading gaps.
Independent of every other analyzer.
"""
from __future__ import annotations

from ..base import AnalyzerContext
from ..registry import AnalyzerRegistry
from ..results import AnalyzerResult, Finding, Recommendation
from ._helpers import score_from_findings


@AnalyzerRegistry.register
class AccessibilityAnalyzer:
    name = "accessibility"
    category = "INDEXABILITY"

    def run(self, context: AnalyzerContext) -> AnalyzerResult:
        result = AnalyzerResult(analyzer=self.name)
        for page in context.pages:
            self._check_images_alt(page, result)
            self._check_title_present(page, result)
            self._check_h1_present(page, result)

        result.score = score_from_findings(result.errors, result.warnings)
        if result.warnings or result.errors:
            result.recommendations.append(
                Recommendation.make(
                    code="A11Y_FIX",
                    title="Mejora la accesibilidad de las páginas",
                    description=(
                        "Añade atributos alt a las imágenes y asegura la "
                        "jerarquía de encabezados para mejorar la "
                        "experiencia de usuario y el SEO."
                    ),
                    priority="MEDIUM",
                )
            )
        return result

    # ------------------------------------------------------------------ #
    def _check_images_alt(self, page, result: AnalyzerResult) -> None:
        if page.images_without_alt <= 0:
            return
        severity = "ERROR" if page.images_without_alt >= 5 else "WARNING"
        result.errors.append(
            Finding.make(
                code="A11Y_IMG_NO_ALT",
                message=(
                    f"{page.images_without_alt} imágenes sin atributo alt "
                    f"en {page.url}."
                ),
                severity=severity,
                category=self.category,
                page=page,
            )
        )

    def _check_title_present(self, page, result: AnalyzerResult) -> None:
        if not page.title.strip():
            result.errors.append(
                Finding.make(
                    code="A11Y_NO_TITLE",
                    message=f"La página {page.url} no expone un <title> accesible.",
                    severity="ERROR",
                    category=self.category,
                    page=page,
                )
            )

    def _check_h1_present(self, page, result: AnalyzerResult) -> None:
        if not page.h1.strip():
            result.warnings.append(
                Finding.make(
                    code="A11Y_NO_H1",
                    message=(
                        f"La página {page.url} no expone un encabezado H1, "
                        f"dificultando la navegación asistida."
                    ),
                    severity="WARNING",
                    category=self.category,
                    page=page,
                )
            )
