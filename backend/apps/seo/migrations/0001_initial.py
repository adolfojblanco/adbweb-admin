"""Initial schema for the SEO module.

Hand-written to match what ``python manage.py makemigrations seo``
would produce on the models defined in ``apps/seo/models.py``.
"""
import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Website",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("domain", models.CharField(max_length=255, unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Sitio web",
                "verbose_name_plural": "Sitios web",
                "ordering": ["name"],
            },
        ),
        migrations.AddIndex(
            model_name="website",
            index=models.Index(
                fields=["is_active"], name="seo_website_active_idx"
            ),
        ),
        migrations.CreateModel(
            name="SEOAudit",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("target_url", models.URLField(max_length=2000)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pendiente"),
                            ("RUNNING", "En curso"),
                            ("COMPLETED", "Completado"),
                            ("FAILED", "Fallido"),
                            ("CANCELLED", "Cancelado"),
                        ],
                        default="PENDING",
                        max_length=16,
                    ),
                ),
                ("max_pages", models.PositiveIntegerField(default=50)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("pages_crawled", models.PositiveIntegerField(default=0)),
                ("issues_count", models.PositiveIntegerField(default=0)),
                (
                    "duration_seconds",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("error_message", models.TextField(blank=True, default="")),
                (
                    "website",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="audits",
                        to="seo.website",
                    ),
                ),
            ],
            options={
                "verbose_name": "Auditoría SEO",
                "verbose_name_plural": "Auditorías SEO",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="seoaudit",
            index=models.Index(
                fields=["website", "-created_at"],
                name="seo_audit_website_created_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="seoaudit",
            index=models.Index(
                fields=["status", "-created_at"],
                name="seo_audit_status_created_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="seoaudit",
            index=models.Index(fields=["status"], name="seo_audit_status_idx"),
        ),
        migrations.CreateModel(
            name="SEOPage",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("url", models.URLField(max_length=2000)),
                ("status_code", models.PositiveIntegerField(default=0)),
                ("title", models.CharField(blank=True, default="", max_length=512)),
                ("meta_description", models.TextField(blank=True, default="")),
                ("h1", models.CharField(blank=True, default="", max_length=512)),
                (
                    "content_type",
                    models.CharField(blank=True, default="", max_length=120),
                ),
                ("content_length", models.PositiveIntegerField(default=0)),
                ("response_time_ms", models.PositiveIntegerField(default=0)),
                ("internal_links", models.PositiveIntegerField(default=0)),
                ("external_links", models.PositiveIntegerField(default=0)),
                ("images_total", models.PositiveIntegerField(default=0)),
                ("images_without_alt", models.PositiveIntegerField(default=0)),
                ("is_indexable", models.BooleanField(default=True)),
                (
                    "audit",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="pages",
                        to="seo.seoaudit",
                    ),
                ),
            ],
            options={
                "verbose_name": "Página SEO",
                "verbose_name_plural": "Páginas SEO",
                "ordering": ["id"],
            },
        ),
        migrations.AddConstraint(
            model_name="seopage",
            constraint=models.UniqueConstraint(
                fields=("audit", "url"),
                name="uniq_seo_page_audit_url",
            ),
        ),
        migrations.AddIndex(
            model_name="seopage",
            index=models.Index(
                fields=["audit", "status_code"],
                name="seo_page_audit_status_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="seopage",
            index=models.Index(
                fields=["audit", "is_indexable"],
                name="seo_page_audit_indexable_idx",
            ),
        ),
        migrations.CreateModel(
            name="SEOIssue",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "severity",
                    models.CharField(
                        choices=[
                            ("INFO", "Info"),
                            ("WARNING", "Advertencia"),
                            ("ERROR", "Error"),
                            ("CRITICAL", "Crítico"),
                        ],
                        max_length=16,
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("META", "Meta etiquetas"),
                            ("HEADINGS", "Encabezados"),
                            ("IMAGES", "Imágenes"),
                            ("LINKS", "Enlaces"),
                            ("PERFORMANCE", "Rendimiento"),
                            ("STATUS", "Estado HTTP"),
                            ("INDEXABILITY", "Indexabilidad"),
                            ("SECURITY", "Seguridad"),
                        ],
                        max_length=24,
                    ),
                ),
                ("code", models.CharField(max_length=64)),
                ("message", models.TextField()),
                (
                    "page",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="issues",
                        to="seo.seopage",
                    ),
                ),
            ],
            options={
                "verbose_name": "Problema SEO",
                "verbose_name_plural": "Problemas SEO",
                "ordering": ["-id"],
            },
        ),
        migrations.AddIndex(
            model_name="seoissue",
            index=models.Index(
                fields=["page", "severity"],
                name="seo_issue_page_severity_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="seoissue",
            index=models.Index(
                fields=["page", "category"],
                name="seo_issue_page_category_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="seoissue",
            index=models.Index(
                fields=["severity", "category"],
                name="seo_issue_sev_cat_idx",
            ),
        ),
        migrations.CreateModel(
            name="SEORecommendation",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=64)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                (
                    "priority",
                    models.CharField(
                        choices=[
                            ("LOW", "Baja"),
                            ("MEDIUM", "Media"),
                            ("HIGH", "Alta"),
                            ("CRITICAL", "Crítica"),
                        ],
                        max_length=16,
                    ),
                ),
                (
                    "page",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="recommendations",
                        to="seo.seopage",
                    ),
                ),
            ],
            options={
                "verbose_name": "Recomendación SEO",
                "verbose_name_plural": "Recomendaciones SEO",
                "ordering": ["-priority", "code"],
            },
        ),
        migrations.AddIndex(
            model_name="seorecommendation",
            index=models.Index(
                fields=["page", "priority"],
                name="seo_rec_page_priority_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="seorecommendation",
            index=models.Index(fields=["priority"], name="seo_rec_priority_idx"),
        ),
        migrations.CreateModel(
            name="SEOScore",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("value", models.PositiveSmallIntegerField()),
                ("breakdown", models.JSONField(blank=True, default=dict)),
                ("computed_at", models.DateTimeField(auto_now=True)),
                (
                    "audit",
                    models.OneToOneField(
                        on_delete=models.deletion.CASCADE,
                        related_name="score",
                        to="seo.seoaudit",
                    ),
                ),
            ],
            options={
                "verbose_name": "Puntuación SEO",
                "verbose_name_plural": "Puntuaciones SEO",
            },
        ),
        migrations.AddIndex(
            model_name="seoscore",
            index=models.Index(fields=["value"], name="seo_score_value_idx"),
        ),
    ]
