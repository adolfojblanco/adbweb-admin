"""
SEO module models.

Self-contained: this module does not import from any other ``apps.*``
package so it can be moved, packaged or removed in isolation.

Domain entities
---------------

* ``Website``           – a domain/website tracked for auditing.
* ``SEOAudit``          – a single execution/run of an SEO audit on a
                          website. Owns its score through a 1:1 link.
* ``SEOPage``           – a page discovered and crawled during an audit.
* ``SEOIssue``          – a finding produced by an analyzer on a page.
* ``SEORecommendation`` – an actionable fix proposed for a page.
* ``SEOScore``          – the aggregate score (0-100) of an audit,
                          with a per-category breakdown.

Lifecycle
---------

``SEOAudit.status`` advances as follows:

    PENDING  →  RUNNING  →  CRAWLED  →  RUNNING  →  COMPLETED
                                  (analyzer)        (or FAILED / CANCELLED)

The crawler stops at ``CRAWLED``; the analyzer pipeline takes it
from there.

Design rules
------------

* All primary keys are UUIDs (no integer leakage, safe to expose in
  URLs and APIs).
* Foreign keys go only one way to avoid duplicated information:

      SEOIssue / SEORecommendation  ──▶  SEOPage  ──▶  SEOAudit  ──▶  Website

  ``SEOIssue`` and ``SEORecommendation`` therefore do **not** carry
  ``page_url`` or ``audit`` denormalized fields; callers join through
  the FK chain.
* ``SEOScore`` is a 1:1 of ``SEOAudit`` so the audit row does not
  duplicate the numeric value.
* ``SEOAudit.pages_crawled`` and ``SEOAudit.issues_count`` are kept
  as pre-computed counters (aggregate stats, not data duplication)
  to avoid N+1 queries in list views.
"""
from __future__ import annotations

import uuid

from django.db import models


class UUIDModel(models.Model):
    """Base model for the SEO module. UUID primary key + timestamps."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Website(UUIDModel):
    name = models.CharField(max_length=160)
    domain = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Sitio web"
        verbose_name_plural = "Sitios web"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["is_active"], name="seo_website_active_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.domain})"


class SEOAudit(UUIDModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendiente"
        RUNNING = "RUNNING", "En curso"
        CRAWLED = "CRAWLED", "Rastreado"
        COMPLETED = "COMPLETED", "Completado"
        FAILED = "FAILED", "Fallido"
        CANCELLED = "CANCELLED", "Cancelado"

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="audits",
    )
    target_url = models.URLField(max_length=2000)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
    )
    max_pages = models.PositiveIntegerField(default=50)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    pages_crawled = models.PositiveIntegerField(default=0)
    issues_count = models.PositiveIntegerField(default=0)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Auditoría SEO"
        verbose_name_plural = "Auditorías SEO"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["website", "-created_at"],
                name="seo_audit_website_created_idx",
            ),
            models.Index(
                fields=["status", "-created_at"],
                name="seo_audit_status_created_idx",
            ),
            models.Index(fields=["status"], name="seo_audit_status_idx"),
        ]

    def __str__(self) -> str:
        return f"Audit {self.pk} ({self.status})"


class SEOPage(UUIDModel):
    audit = models.ForeignKey(
        SEOAudit,
        on_delete=models.CASCADE,
        related_name="pages",
    )
    url = models.URLField(max_length=2000)
    status_code = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=512, blank=True, default="")
    meta_description = models.TextField(blank=True, default="")
    h1 = models.CharField(max_length=512, blank=True, default="")
    content_type = models.CharField(max_length=120, blank=True, default="")
    content_length = models.PositiveIntegerField(default=0)
    response_time_ms = models.PositiveIntegerField(default=0)
    internal_links = models.PositiveIntegerField(default=0)
    external_links = models.PositiveIntegerField(default=0)
    images_total = models.PositiveIntegerField(default=0)
    images_without_alt = models.PositiveIntegerField(default=0)
    is_indexable = models.BooleanField(default=True)
    canonical_url = models.URLField(max_length=2000, blank=True, null=True)
    redirect_count = models.PositiveIntegerField(default=0)
    raw_html = models.TextField(blank=True, default="")
    crawled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Página SEO"
        verbose_name_plural = "Páginas SEO"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["audit", "url"],
                name="uniq_seo_page_audit_url",
            ),
        ]
        indexes = [
            models.Index(
                fields=["audit", "status_code"],
                name="seo_page_audit_status_idx",
            ),
            models.Index(
                fields=["audit", "is_indexable"],
                name="seo_page_audit_indexable_idx",
            ),
        ]

    def __str__(self) -> str:
        return self.url


class SEOIssue(UUIDModel):
    class Severity(models.TextChoices):
        INFO = "INFO", "Info"
        WARNING = "WARNING", "Advertencia"
        ERROR = "ERROR", "Error"
        CRITICAL = "CRITICAL", "Crítico"

    class Category(models.TextChoices):
        META = "META", "Meta etiquetas"
        HEADINGS = "HEADINGS", "Encabezados"
        IMAGES = "IMAGES", "Imágenes"
        LINKS = "LINKS", "Enlaces"
        PERFORMANCE = "PERFORMANCE", "Rendimiento"
        STATUS = "STATUS", "Estado HTTP"
        INDEXABILITY = "INDEXABILITY", "Indexabilidad"
        SECURITY = "SECURITY", "Seguridad"

    page = models.ForeignKey(
        SEOPage,
        on_delete=models.CASCADE,
        related_name="issues",
    )
    severity = models.CharField(max_length=16, choices=Severity.choices)
    category = models.CharField(max_length=24, choices=Category.choices)
    code = models.CharField(max_length=64)
    message = models.TextField()

    class Meta:
        verbose_name = "Problema SEO"
        verbose_name_plural = "Problemas SEO"
        ordering = ["-id"]
        indexes = [
            models.Index(
                fields=["page", "severity"],
                name="seo_issue_page_severity_idx",
            ),
            models.Index(
                fields=["page", "category"],
                name="seo_issue_page_category_idx",
            ),
            models.Index(
                fields=["severity", "category"],
                name="seo_issue_sev_cat_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"[{self.severity}] {self.code}"


class SEORecommendation(UUIDModel):
    class Priority(models.TextChoices):
        LOW = "LOW", "Baja"
        MEDIUM = "MEDIUM", "Media"
        HIGH = "HIGH", "Alta"
        CRITICAL = "CRITICAL", "Crítica"

    page = models.ForeignKey(
        SEOPage,
        on_delete=models.CASCADE,
        related_name="recommendations",
    )
    code = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=16, choices=Priority.choices)

    class Meta:
        verbose_name = "Recomendación SEO"
        verbose_name_plural = "Recomendaciones SEO"
        ordering = ["-priority", "code"]
        indexes = [
            models.Index(
                fields=["page", "priority"],
                name="seo_rec_page_priority_idx",
            ),
            models.Index(fields=["priority"], name="seo_rec_priority_idx"),
        ]

    def __str__(self) -> str:
        return self.title


class SEOScore(UUIDModel):
    """Aggregate score of an audit (0-100) with a per-category breakdown."""

    audit = models.OneToOneField(
        SEOAudit,
        on_delete=models.CASCADE,
        related_name="score",
    )
    value = models.PositiveSmallIntegerField()
    breakdown = models.JSONField(default=dict, blank=True)
    computed_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Puntuación SEO"
        verbose_name_plural = "Puntuaciones SEO"
        indexes = [
            models.Index(fields=["value"], name="seo_score_value_idx"),
        ]

    def __str__(self) -> str:
        return str(self.value)


class LighthouseResult(UUIDModel):
    """Lighthouse audit of a single page.

    Stores the four category scores and the six core web-vital
    metrics emitted by Lighthouse. The ``audit`` is reachable
    through ``page.audit`` to avoid duplicating the relation.
    """

    page = models.ForeignKey(
        SEOPage,
        on_delete=models.CASCADE,
        related_name="lighthouse_results",
    )

    # Category scores (0-100, rounded from Lighthouse 0.0-1.0)
    performance_score = models.PositiveSmallIntegerField(null=True, blank=True)
    accessibility_score = models.PositiveSmallIntegerField(null=True, blank=True)
    seo_score = models.PositiveSmallIntegerField(null=True, blank=True)
    best_practices_score = models.PositiveSmallIntegerField(null=True, blank=True)

    # Core Web Vitals + supporting metrics. Units follow Lighthouse
    # conventions: CLS is unitless, the rest are milliseconds.
    cls = models.FloatField(null=True, blank=True)
    lcp = models.FloatField(null=True, blank=True)
    inp = models.FloatField(null=True, blank=True)
    fcp = models.FloatField(null=True, blank=True)
    ttfb = models.FloatField(null=True, blank=True)
    speed_index = models.FloatField(null=True, blank=True)

    # Run metadata
    lighthouse_version = models.CharField(max_length=32, blank=True, default="")
    user_agent = models.CharField(max_length=512, blank=True, default="")
    run_at = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Resultado Lighthouse"
        verbose_name_plural = "Resultados Lighthouse"
        ordering = ["-run_at"]
        indexes = [
            models.Index(fields=["page", "-run_at"], name="seo_lh_page_run_idx"),
        ]

    def __str__(self) -> str:
        return f"Lighthouse {self.page.url} @ {self.run_at:%Y-%m-%d %H:%M}"
