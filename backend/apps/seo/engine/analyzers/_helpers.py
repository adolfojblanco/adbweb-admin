"""
Shared helpers for analyzers.

The helpers here are intentionally minimal: they do not perform any
analysis. They just centralize the "start at 100, penalize per
issue" pattern that every analyzer uses to compute its own score
without leaking business rules into the orchestrator.
"""
from __future__ import annotations

from typing import Iterable

# Penalties applied per finding severity. Analyzers MAY override
# these locally if they need a different curve; the constants exist
# so the default behavior is consistent across analyzers.
PENALTY_PER_ERROR = 8
PENALTY_PER_WARNING = 3
MIN_SCORE = 0
MAX_SCORE = 100


def clamp(value: int, lo: int = MIN_SCORE, hi: int = MAX_SCORE) -> int:
    return max(lo, min(hi, value))


def score_from_findings(
    errors: Iterable,
    warnings: Iterable,
    *,
    penalty_error: int = PENALTY_PER_ERROR,
    penalty_warning: int = PENALTY_PER_WARNING,
) -> int:
    """Compute an analyzer score from its findings.

    Score starts at 100 and decreases linearly. The penalty values
    are tuned so an analyzer with 5 errors and 10 warnings lands
    near 30.
    """
    score = MAX_SCORE - penalty_error * len(list(errors)) - penalty_warning * len(list(warnings))
    return clamp(score)
