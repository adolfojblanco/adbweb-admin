"""
Registry for SEO analyzers.

Analyzers are registered on import via the :meth:`AnalyzerRegistry.register`
decorator. The engine pulls the list of analyzers through
:meth:`AnalyzerRegistry.all`; analyzers are NOT auto-discovered by
importing the package – the ``engine.analyzers`` package triggers
registration explicitly by importing each module.
"""
from __future__ import annotations

from typing import Iterable, List, Type

from .base import BaseAnalyzer


class AnalyzerRegistry:
    _analyzers: List[Type[BaseAnalyzer]] = []

    @classmethod
    def register(cls, analyzer_cls: Type[BaseAnalyzer]) -> Type[BaseAnalyzer]:
        if analyzer_cls in cls._analyzers:
            return analyzer_cls
        cls._analyzers.append(analyzer_cls)
        return analyzer_cls

    @classmethod
    def all(cls) -> Iterable[Type[BaseAnalyzer]]:
        return tuple(cls._analyzers)

    @classmethod
    def clear(cls) -> None:
        """Test hook. Wipes the registry between test cases."""
        cls._analyzers = []
