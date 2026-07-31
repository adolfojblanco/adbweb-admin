"""Tests for the SEO model layer."""
from django.test import TestCase

from apps.seo.models import (
    SEOAudit,
    SEOIssue,
    SEOPage,
    SEORecommendation,
    SEOScore,
    Website,
)


class SeoModelTests(TestCase):
    def setUp(self):
        self.website = Website.objects.create(name="Demo", domain="demo.com")
        self.audit = SEOAudit.objects.create(
            website=self.website,
            target_url="https://demo.com/",
        )
        self.page = SEOPage.objects.create(
            audit=self.audit,
            url="https://demo.com/",
            status_code=200,
        )

    def test_website_str(self):
        self.assertEqual(str(self.website), "Demo (demo.com)")

    def test_website_domain_unique(self):
        with self.assertRaises(Exception):
            Website.objects.create(name="Other", domain="demo.com")

    def test_audit_default_status(self):
        self.assertEqual(self.audit.status, SEOAudit.Status.PENDING)

    def test_audit_website_cascade(self):
        wid = self.website.id
        self.website.delete()
        self.assertFalse(SEOAudit.objects.filter(id=self.audit.id).exists())
        self.assertFalse(Website.objects.filter(id=wid).exists())

    def test_page_unique_per_audit(self):
        with self.assertRaises(Exception):
            SEOPage.objects.create(
                audit=self.audit,
                url="https://demo.com/",
                status_code=200,
            )

    def test_issue_persists_with_page_fk(self):
        issue = SEOIssue.objects.create(
            page=self.page,
            severity=SEOIssue.Severity.WARNING,
            category=SEOIssue.Category.META,
            code="TEST",
            message="hello",
        )
        self.assertEqual(issue.page_id, self.page.id)
        # No denormalized page_url or audit fields exist on SEOIssue.
        self.assertNotIn("page_url", [f.name for f in issue._meta.get_fields()])
        self.assertNotIn("audit", [f.name for f in issue._meta.get_fields()])

    def test_recommendation_persists_with_page_fk(self):
        rec = SEORecommendation.objects.create(
            page=self.page,
            code="META_DESCRIPTION",
            title="Add meta description",
            description="Write a 160-char meta description.",
            priority=SEORecommendation.Priority.MEDIUM,
        )
        self.assertEqual(rec.page_id, self.page.id)

    def test_score_is_one_to_one_per_audit(self):
        SEOScore.objects.create(audit=self.audit, value=85, breakdown={"META": 90})
        with self.assertRaises(Exception):
            SEOScore.objects.create(audit=self.audit, value=42)
