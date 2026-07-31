"""
SEO module selectors.

Read-side queries live here so viewsets stay thin and we can reuse the
same optimized lookups across the API, admin and Celery tasks.
"""
from __future__ import annotations

# Intentionally empty: real selectors (list_audits_for_project,
# issues_by_severity, score_distribution, ...) will be defined here.
