"""Crawler configuration."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CrawlerSettings:
    """Settings consumed by :class:`Fetcher` and :class:`Crawler`."""

    timeout_ms: int = 30_000
    headless: bool = True
    max_pages: int = 50
    user_agent: str = (
        "Mozilla/5.0 (compatible; ADBWebBot/1.0; +https://adbwebdesign.com/bot)"
    )

    @classmethod
    def from_audit(cls, audit) -> "CrawlerSettings":
        """Build a settings object from an ``SEOAudit`` instance."""
        return cls(max_pages=audit.max_pages)
