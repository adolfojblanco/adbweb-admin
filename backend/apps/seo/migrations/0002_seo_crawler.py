"""Crawler-related schema changes.

* Adds the ``CRAWLED`` value to ``SEOAudit.Status``.
* Adds the crawl payload to ``SEOPage``: ``crawled_at``,
  ``raw_html``, ``canonical_url`` and ``redirect_count``.
"""
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("seo", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="seoaudit",
            name="status",
            field=models.CharField(
                choices=[
                    ("PENDING", "Pendiente"),
                    ("RUNNING", "En curso"),
                    ("CRAWLED", "Rastreado"),
                    ("COMPLETED", "Completado"),
                    ("FAILED", "Fallido"),
                    ("CANCELLED", "Cancelado"),
                ],
                default="PENDING",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="seopage",
            name="canonical_url",
            field=models.URLField(blank=True, max_length=2000, null=True),
        ),
        migrations.AddField(
            model_name="seopage",
            name="redirect_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="seopage",
            name="raw_html",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="seopage",
            name="crawled_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
