from django.db import models
from apps.core.models import TimeStampedModel
from apps.accounts.models import CustomerUser, User

# SEO models here.

class SeoProject(TimeStampedModel):
    """
    Representa el proyecto SEO de la empresa
    """
    client = models.ForeignKey(CustomerUser,
                               on_delete=models.SET_NULL,
                               related_name="seo_project",
                               null=True,
                               blank=True
                            )
    domain = models.URLField()
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User,
                                   on_delete=models.SET_NULL,
                                   null=True,
                                   blank=True,
                                   related_name="seo_project_created_by"
                                )

    class Meta:
        verbose_name_plural = "Proyectos SEO"
        verbose_name = "Proyecto SEO"
        ordering = ["-domain"]

    def __str__(self):
        return f"{self.client.billing_name} - {self.domain}"

class SeoUrl(TimeStampedModel):
    """
    Pagina especificada de la URL SEO de la empresa
    """
    PAGE_TYPE_CHOICES = [
        ("home", "Home Page"),
        ("services", "Services Page"),
        ("blog", "Blogs Post"),
        ("landing", "Landing PAge"),
        ("contact", "Contact Page"),
        ("other", "Other"),
    ]
    project = models.ForeignKey(SeoProject, on_delete=models.CASCADE, related_name="urls")
    url = models.URLField()
    page_type = models.CharField(max_length=20, choices=PAGE_TYPE_CHOICES, default="other")
    label = models.CharField(max_length=255, help_text="Nombre interno, identificación de pagina")
    is_primary = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True, help_text="Notas del administrador")

    class Meta:
        verbose_name_plural = "SEO Urls"
        verbose_name = "SEO Url"
        ordering = ["project", "url"]
        unique_together = ["project", "url"]

        def __str__(self):
            return self.label or self.url


class SeoAudit(TimeStampedModel):
    """Representa la auditoria SEO sobre una url"""
    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("running", "Corriendo"),
        ("completed", "Completado"),
        ("failed", "Errores"),
    ]

    seo_url = models.ForeignKey(SeoUrl, on_delete=models.CASCADE, related_name="audits")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    seo_score = models.PositiveIntegerField(default=0, help_text="Puntuación SEO general del 0 al 100")
    status_code = models.PositiveIntegerField(default=0, help_text="Código HTTP")
    title = models.TextField(blank=True)
    title_length = models.PositiveIntegerField(default=0)
    meta_description = models.TextField(blank=True, null=True)
    meta_description_length = models.PositiveIntegerField(default=0)

    h1 = models.TextField(blank=True, null=True)
    h1_count = models.PositiveIntegerField(default=0)
    h1_length = models.PositiveIntegerField(default=0)

    images_total = models.PositiveIntegerField(default=0)
    images_without_alt = models.PositiveIntegerField(default=0)

    internal_links = models.TextField(blank=True, null=True)
    external_links = models.TextField(blank=True, null=True)

    canonical = models.URLField(blank=True, null=True)

    has_sitemap = models.BooleanField(default=False)
    has_robots_txt = models.BooleanField(default=False)
    has_schema = models.BooleanField(default=False)

    error_message = models.TextField(blank=True, null=True)

    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "SEO Auditorias"
        verbose_name = "SEO Auditoria"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Autidoria {self.seo_url.url} - {self.created_at}"


class SeoIssue(TimeStampedModel):
    """
    Problema SEO detectado dentro de una auditoría.
    """

    SEVERITY_CHOICES = [
        ("critical", "Critical"),
        ("warning", "Warning"),
        ("opportunity", "Opportunity"),
    ]

    CATEGORY_CHOICES = [
        ("technical", "Technical SEO"),
        ("content", "Content"),
        ("performance", "Performance"),
        ("accessibility", "Accessibility"),
        ("indexing", "Indexing"),
        ("links", "Links"),
        ("schema", "Schema"),
        ("other", "Other"),
    ]

    audit = models.ForeignKey(
        "seo.SeoAudit",
        on_delete=models.CASCADE,
        related_name="issues"
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="other"
    )

    issue_type = models.CharField(
        max_length=100,
        help_text="Tipo interno del problema. Ej: missing_meta_description."
    )

    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES
    )

    title = models.CharField(
        max_length=255,
        help_text="Título corto del problema."
    )

    description = models.TextField(
        help_text="Explicación del problema detectado."
    )

    recommendation = models.TextField(
        blank=True,
        help_text="Qué se recomienda hacer para solucionarlo."
    )

    is_fixed = models.BooleanField(
        default=False,
        help_text="Marca si el problema ya fue solucionado."
    )

    fixed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    visible_to_client = models.BooleanField(
        default=True,
        help_text="Controla si este problema se muestra al cliente."
    )

    class Meta:
        verbose_name = "SEO Issue"
        verbose_name_plural = "SEO Issues"
        ordering = ["severity", "-created_at"]

    def _str_(self):
        return self.title


class PageSpeedResult(TimeStampedModel):
    """
    Resultado de velocidad y Core Web Vitals para una auditoría SEO.
    Normalmente estos datos vendrán de Google PageSpeed Insights API.
    """

    audit = models.OneToOneField(
        "seo.SeoAudit",
        on_delete=models.CASCADE,
        related_name="pagespeed"
    )

    mobile_score = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Puntuación de rendimiento móvil de 0 a 100."
    )

    desktop_score = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Puntuación de rendimiento escritorio de 0 a 100."
    )

    lcp = models.FloatField(
        null=True,
        blank=True,
        help_text="Largest Contentful Paint en segundos."
    )

    inp = models.FloatField(
        null=True,
        blank=True,
        help_text="Interaction to Next Paint en milisegundos."
    )

    cls = models.FloatField(
        null=True,
        blank=True,
        help_text="Cumulative Layout Shift."
    )

    fcp = models.FloatField(
        null=True,
        blank=True,
        help_text="First Contentful Paint en segundos."
    )

    ttfb = models.FloatField(
        null=True,
        blank=True,
        help_text="Time To First Byte en segundos."
    )

    speed_index = models.FloatField(
        null=True,
        blank=True,
        help_text="Speed Index en segundos."
    )

    total_blocking_time = models.FloatField(
        null=True,
        blank=True,
        help_text="Total Blocking Time en milisegundos."
    )

    raw_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Respuesta completa o parcial de PageSpeed API."
    )

    class Meta:
        verbose_name = "PageSpeed Result"
        verbose_name_plural = "PageSpeed Results"

    def _str_(self):
        return f"PageSpeed - {self.audit.seo_url.url}"

class AiSeoRecommendation(TimeStampedModel):
    """
    Recomendaciones SEO generadas por IA
    utilizando los datos de una auditoría.
    """

    audit = models.OneToOneField(
        "seo.SeoAudit",
        on_delete=models.CASCADE,
        related_name="ai_recommendation"
    )

    summary = models.TextField(
        help_text="Resumen general del análisis SEO."
    )

    priority_actions = models.JSONField(
        default=list,
        blank=True,
        help_text="Lista de acciones prioritarias."
    )

    strengths = models.JSONField(
        default=list,
        blank=True,
        help_text="Aspectos positivos detectados."
    )

    weaknesses = models.JSONField(
        default=list,
        blank=True,
        help_text="Debilidades detectadas."
    )

    client_explanation = models.TextField(
        blank=True,
        help_text="Explicación simplificada para el cliente."
    )

    admin_notes = models.TextField(
        blank=True,
        help_text="Notas técnicas internas visibles solo para administradores."
    )

    estimated_impact = models.CharField(
        max_length=100,
        blank=True,
        help_text="Impacto esperado de las mejoras."
    )

    estimated_difficulty = models.CharField(
        max_length=100,
        blank=True,
        help_text="Nivel de dificultad de implementación."
    )

    visible_to_client = models.BooleanField(
        default=True
    )

    class Meta:
        verbose_name = "AI SEO Recommendation"
        verbose_name_plural = "AI SEO Recommendations"

    def _str_(self):
        return f"AI Recommendation - {self.audit.seo_url.url}"

class SeoOptimization(TimeStampedModel):
    """
    Mejora SEO realizada o planificada dentro de un proyecto.
    Sirve para mostrar progreso al cliente y comparar antes/después.
    """

    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    CATEGORY_CHOICES = [
        ("technical", "Technical SEO"),
        ("content", "Content"),
        ("performance", "Performance"),
        ("accessibility", "Accessibility"),
        ("indexing", "Indexing"),
        ("links", "Links"),
        ("schema", "Schema"),
        ("other", "Other"),
    ]

    project = models.ForeignKey(
        "seo.SeoProject",
        on_delete=models.CASCADE,
        related_name="optimizations"
    )

    seo_url = models.ForeignKey(
        "seo.SeoUrl",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="optimizations",
        help_text="URL específica relacionada con esta optimización, si aplica."
    )

    related_issue = models.ForeignKey(
        "seo.SeoIssue",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="optimizations",
        help_text="Problema SEO que esta optimización intenta solucionar."
    )

    title = models.CharField(max_length=255)

    description = models.TextField(
        help_text="Explicación de la mejora realizada o planificada."
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="other"
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="planned"
    )

    before_value = models.TextField(
        blank=True,
        help_text="Estado antes de la optimización."
    )

    after_value = models.TextField(
        blank=True,
        help_text="Estado después de la optimización."
    )

    result_summary = models.TextField(
        blank=True,
        help_text="Resumen del resultado obtenido."
    )

    visible_to_client = models.BooleanField(
        default=True,
        help_text="Controla si esta optimización se muestra en el panel cliente."
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "SEO Optimization"
        verbose_name_plural = "SEO Optimizations"
        ordering = ["-created_at"]

    def _str_(self):
        return self.title
