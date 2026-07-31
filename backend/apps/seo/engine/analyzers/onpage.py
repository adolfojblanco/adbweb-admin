"""On-page SEO analyzer.

Inspects the content surface of each page: title, meta description
and heading structure. Independent of every other analyzer.
"""
from __future__ import annotations

from ..base import AnalyzerContext
from ..registry import AnalyzerRegistry
from ..results import AnalyzerResult, Finding, Recommendation
from ._helpers import score_from_findings


@AnalyzerRegistry.register
class OnPageAnalyzer:
    name = "onpage"
    category = "META"

    TITLE_MIN = 30
    TITLE_MAX = 65
    META_MIN = 70
    META_MAX = 160

    def run(self, context: AnalyzerContext) -> AnalyzerResult:
        result = AnalyzerResult(analyzer=self.name)
        for page in context.pages:
            self._check_title(page, result)
            self._check_meta_description(page, result)
            self._check_h1(page, result)

        result.score = score_from_findings(result.errors, result.warnings)
        if result.errors:
            result.recommendations.append(
                Recommendation.make(
                    code="ONPAGE_META",
                    title="Optimiza las meta-etiquetas de tus páginas",
                    description=(
                        "Varias páginas carecen de título, meta description "
                        "o encabezado H1. Ajusta la longitud y unicidad de "
                        "estos campos para mejorar el CTR en buscadores."
                    ),
                    priority="HIGH",
                )
            )
        return result

    # ------------------------------------------------------------------ #
    def _check_title(self, page, result: AnalyzerResult) -> None:
        if not page.title.strip():
            result.errors.append(
                Finding.make(
                    code="ONPAGE_NO_TITLE",
                    message=f"La página {page.url} no tiene <title>.",
                    severity="ERROR",
                    category="META",
                    page=page,
                )
            )
            return
        length = len(page.title)
        if length < self.TITLE_MIN:
            result.warnings.append(
                Finding.make(
                    code="ONPAGE_SHORT_TITLE",
                    message=(
                        f"Título demasiado corto ({length} chars) en {page.url}."
                    ),
                    severity="WARNING",
                    category="META",
                    page=page,
                )
            )
        elif length > self.TITLE_MAX:
            result.warnings.append(
                Finding.make(
                    code="ONPAGE_LONG_TITLE",
                    message=(
                        f"Título demasiado largo ({length} chars) en {page.url}."
                    ),
                    severity="WARNING",
                    category="META",
                    page=page,
                )
            )

    def _check_meta_description(self, page, result: AnalyzerResult) -> None:
        if not page.meta_description.strip():
            result.warnings.append(
                Finding.make(
                    code="ONPAGE_NO_META",
                    message=f"La página {page.url} no tiene meta description.",
                    severity="WARNING",
                    category="META",
                    page=page,
                )
            )
            return
        length = len(page.meta_description)
        if length < self.META_MIN or length > self.META_MAX:
            result.warnings.append(
                Finding.make(
                    code="ONPAGE_META_LENGTH",
                    message=(
                        f"Meta description fuera de rango ({length} chars) "
                        f"en {page.url}."
                    ),
                    severity="WARNING",
                    category="META",
                    page=page,
                )
            )

    def _check_h1(self, page, result: AnalyzerResult) -> None:
        if not page.h1.strip():
            result.warnings.append(
                Finding.make(
                    code="ONPAGE_NO_H1",
                    message=f"La página {page.url} no tiene encabezado H1.",
                    severity="WARNING",
                    category="HEADINGS",
                    page=page,
                )
            )
