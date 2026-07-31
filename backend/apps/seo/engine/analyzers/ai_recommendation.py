"""AI recommendation engine.

Generates actionable, human-readable recommendations for every
page. The engine does NOT consume the output of the other
analyzers: it inspects the audit data on its own and produces its
own score, errors, warnings and recommendations.

In production this is the place where a real LLM call would
replace the template-based generator. The interface stays the
same: receive an :class:`AnalyzerContext` and return an
:class:`AnalyzerResult`.
"""
from __future__ import annotations

from ..base import AnalyzerContext
from ..registry import AnalyzerRegistry
from ..results import AnalyzerResult, Finding, Recommendation
from ._helpers import clamp


@AnalyzerRegistry.register
class AIRecommendationEngine:
    name = "ai_recommendation"
    category = "META"

    MAX_RECOMMENDATIONS_PER_PAGE = 5
    PENALTY_PER_RECOMMENDATION = 6

    def run(self, context: AnalyzerContext) -> AnalyzerResult:
        result = AnalyzerResult(analyzer=self.name)
        for page in context.pages:
            page_recs = self._build_recommendations_for(page)
            # Trim so the AI engine never produces more than N per page.
            page_recs = page_recs[: self.MAX_RECOMMENDATIONS_PER_PAGE]
            result.recommendations.extend(page_recs)

            for rec in page_recs:
                if rec.priority in {"HIGH", "CRITICAL"}:
                    result.errors.append(
                        Finding.make(
                            code=f"AI_{rec.code}",
                            message=rec.title,
                            severity="WARNING",
                            category=self.category,
                            page=page,
                        )
                    )
                else:
                    result.warnings.append(
                        Finding.make(
                            code=f"AI_{rec.code}",
                            message=rec.title,
                            severity="INFO",
                            category=self.category,
                            page=page,
                        )
                    )

        result.score = self._score(len(result.recommendations), pages=len(list(context.pages)))
        return result

    # ------------------------------------------------------------------ #
    def _build_recommendations_for(self, page) -> list[Recommendation]:
        recs: list[Recommendation] = []

        if not page.title.strip():
            recs.append(
                Recommendation.make(
                    code="ADD_TITLE",
                    title="Añade un <title> descriptivo y único",
                    description=(
                        "Define un título de 30-65 caracteres que describa "
                        "el contenido principal de la página."
                    ),
                    priority="HIGH",
                    page=page,
                )
            )
        elif len(page.title) > 65:
            recs.append(
                Recommendation.make(
                    code="SHORTEN_TITLE",
                    title="Acorta el <title> para evitar truncamientos",
                    description=(
                        "Los títulos por encima de 65 caracteres se cortan "
                        "en los resultados de búsqueda."
                    ),
                    priority="MEDIUM",
                    page=page,
                )
            )

        if not page.meta_description.strip():
            recs.append(
                Recommendation.make(
                    code="ADD_META_DESCRIPTION",
                    title="Añade una meta description de 70-160 caracteres",
                    description=(
                        "Una meta description atractiva mejora el CTR desde "
                        "los resultados de búsqueda."
                    ),
                    priority="MEDIUM",
                    page=page,
                )
            )

        if not page.h1.strip():
            recs.append(
                Recommendation.make(
                    code="ADD_H1",
                    title="Incluye un encabezado H1 que resuma la página",
                    description=(
                        "El H1 ayuda a usuarios y motores a entender la "
                        "jerarquía del contenido."
                    ),
                    priority="MEDIUM",
                    page=page,
                )
            )

        if page.images_without_alt > 0:
            recs.append(
                Recommendation.make(
                    code="FIX_IMAGE_ALT",
                    title=f"Añade atributo alt a {page.images_without_alt} imágenes",
                    description=(
                        "Las imágenes sin texto alternativo penalizan la "
                        "accesibilidad y el SEO de imágenes."
                    ),
                    priority="MEDIUM",
                    page=page,
                )
            )

        if page.response_time_ms >= 1500:
            recs.append(
                Recommendation.make(
                    code="IMPROVE_RESPONSE_TIME",
                    title="Reduce el tiempo de respuesta del servidor",
                    description=(
                        "Apunta a un TTFB por debajo de 600 ms; considera "
                        "caché, CDN y optimización de la base de datos."
                    ),
                    priority="HIGH",
                    page=page,
                )
            )

        return recs

    def _score(self, rec_count: int, *, pages: int) -> int:
        if pages == 0:
            return 100
        density = rec_count / pages
        return clamp(100 - int(density * self.PENALTY_PER_RECOMMENDATION))
