"""Add ``LighthouseResult`` for the Lighthouse integration."""
import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("seo", "0002_seo_crawler"),
    ]

    operations = [
        migrations.CreateModel(
            name="LighthouseResult",
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
                    "performance_score",
                    models.PositiveSmallIntegerField(blank=True, null=True),
                ),
                (
                    "accessibility_score",
                    models.PositiveSmallIntegerField(blank=True, null=True),
                ),
                (
                    "seo_score",
                    models.PositiveSmallIntegerField(blank=True, null=True),
                ),
                (
                    "best_practices_score",
                    models.PositiveSmallIntegerField(blank=True, null=True),
                ),
                ("cls", models.FloatField(blank=True, null=True)),
                ("lcp", models.FloatField(blank=True, null=True)),
                ("inp", models.FloatField(blank=True, null=True)),
                ("fcp", models.FloatField(blank=True, null=True)),
                ("ttfb", models.FloatField(blank=True, null=True)),
                ("speed_index", models.FloatField(blank=True, null=True)),
                (
                    "lighthouse_version",
                    models.CharField(blank=True, default="", max_length=32),
                ),
                (
                    "user_agent",
                    models.CharField(blank=True, default="", max_length=512),
                ),
                ("run_at", models.DateTimeField(auto_now_add=True)),
                ("error_message", models.TextField(blank=True, default="")),
                (
                    "page",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="lighthouse_results",
                        to="seo.seopage",
                    ),
                ),
            ],
            options={
                "verbose_name": "Resultado Lighthouse",
                "verbose_name_plural": "Resultados Lighthouse",
                "ordering": ["-run_at"],
            },
        ),
        migrations.AddIndex(
            model_name="lighthouseresult",
            index=models.Index(
                fields=["page", "-run_at"],
                name="seo_lh_page_run_idx",
            ),
        ),
    ]
