"""Parse Lighthouse JSON output into a flat :class:`LighthouseReport`."""
from __future__ import annotations

from dataclasses import dataclass, field


# Mapping from the user-facing metric name to the audit id that
# Lighthouse uses in the JSON. Some metrics changed ids across
# versions (INP was added in Lighthouse 10); we accept any alias.
METRIC_AUDIT_KEYS: dict[str, tuple[str, ...]] = {
    "cls": ("cumulative-layout-shift",),
    "lcp": ("largest-contentful-paint",),
    "inp": ("interaction-to-next-paint",),
    "fcp": ("first-contentful-paint",),
    "ttfb": ("server-response-time",),
    "speed_index": ("speed-index",),
}

CATEGORY_KEYS: dict[str, str] = {
    "performance": "performance",
    "accessibility": "accessibility",
    "seo": "seo",
    "best_practices": "best-practices",
}


@dataclass
class LighthouseReport:
    """Flat representation of one Lighthouse run."""

    url: str
    final_url: str
    lighthouse_version: str
    user_agent: str
    performance: int | None
    accessibility: int | None
    seo: int | None
    best_practices: int | None
    cls: float | None
    lcp: float | None
    inp: float | None
    fcp: float | None
    ttfb: float | None
    speed_index: float | None
    error: str | None = None
    raw: dict = field(default_factory=dict)


def parse_lighthouse_report(url: str, data: dict) -> LighthouseReport:
    """Extract scores and metrics from a Lighthouse JSON document."""
    categories = data.get("categories") or {}
    audits = data.get("audits") or {}

    def score(slug: str) -> int | None:
        cat = categories.get(slug) or {}
        if cat.get("score") is None:
            return None
        return round(float(cat["score"]) * 100)

    def metric(name: str) -> float | None:
        for key in METRIC_AUDIT_KEYS[name]:
            audit = audits.get(key)
            if audit is None:
                continue
            value = audit.get("numericValue")
            if value is None:
                continue
            return float(value)
        return None

    return LighthouseReport(
        url=url,
        final_url=(
            data.get("finalDisplayedUrl")
            or data.get("finalUrl")
            or data.get("requestedUrl")
            or url
        ),
        lighthouse_version=data.get("lighthouseVersion", ""),
        user_agent=data.get("userAgent", ""),
        performance=score(CATEGORY_KEYS["performance"]),
        accessibility=score(CATEGORY_KEYS["accessibility"]),
        seo=score(CATEGORY_KEYS["seo"]),
        best_practices=score(CATEGORY_KEYS["best_practices"]),
        cls=metric("cls"),
        lcp=metric("lcp"),
        inp=metric("inp"),
        fcp=metric("fcp"),
        ttfb=metric("ttfb"),
        speed_index=metric("speed_index"),
        raw=data,
    )
