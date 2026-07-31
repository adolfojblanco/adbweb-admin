"""
Built-in SEO analyzers.

Importing this package has the side effect of registering every
analyzer with :class:`AnalyzerRegistry`. The :class:`AuditEngine`
imports the package to ensure registration runs at startup.
"""
from .accessibility import AccessibilityAnalyzer
from .ai_recommendation import AIRecommendationEngine
from .onpage import OnPageAnalyzer
from .performance import PerformanceAnalyzer
from .technical import TechnicalAnalyzer

__all__ = [
    "AccessibilityAnalyzer",
    "AIRecommendationEngine",
    "OnPageAnalyzer",
    "PerformanceAnalyzer",
    "TechnicalAnalyzer",
]
