"""
SEO audit engine.

The engine is the orchestrator that runs every registered analyzer
against an audit and aggregates their results. It is consumed
exclusively through ``apps.seo.services``; views must not call into
the engine directly.

Analyzers live in :mod:`apps.seo.engine.analyzers`. Each one is an
independent unit that receives an :class:`AnalyzerContext` and
returns an :class:`AnalyzerResult`. New analyzers are added by:

1. Implementing :class:`BaseAnalyzer`.
2. Decorating the class with ``@AnalyzerRegistry.register``.
3. Importing the module from :mod:`apps.seo.engine.analyzers` so
   registration runs on application startup.
"""
from .base import AnalyzerContext, BaseAnalyzer
from .orchestrator import AuditEngine
from .registry import AnalyzerRegistry
from .results import (
    AnalyzerResult,
    AuditResult,
    Finding,
    Recommendation,
)

__all__ = [
    "AnalyzerContext",
    "AnalyzerResult",
    "AnalyzerRegistry",
    "AuditEngine",
    "AuditResult",
    "BaseAnalyzer",
    "Finding",
    "Recommendation",
]
