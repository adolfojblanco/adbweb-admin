"""
Base classes for SEO analyzers.

An analyzer is a self-contained unit of work that inspects the
data of one audit and returns an :class:`AnalyzerResult`. The
:class:`AnalyzerContext` is the only input; analyzers do not share
state with each other and they MUST NOT look at the results of
sibling analyzers.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol

from ..models import SEOAudit
from .results import AnalyzerResult


@dataclass
class AnalyzerContext:
    """Read-only context handed to every analyzer.

    Analyzers pull the page list through the ``pages`` property.
    Each access hits the database, so analyzers are encouraged to
    materialize the queryset once per ``run`` call.
    """

    audit: SEOAudit

    @property
    def pages(self) -> Iterable:
        return self.audit.pages.all()

    @property
    def website(self) -> "SEOAudit.website":  # type: ignore[name-defined]
        return self.audit.website


class BaseAnalyzer(Protocol):
    """Protocol every analyzer satisfies.

    Concrete analyzers declare:

    * ``name``     – short identifier used for logs and metrics.
    * ``category`` – one of :class:`apps.seo.models.SEOIssue.Category`.
    * ``run``      – receives an :class:`AnalyzerContext` and returns
      an :class:`AnalyzerResult`.
    """

    name: str
    category: str

    def run(self, context: AnalyzerContext) -> AnalyzerResult: ...
