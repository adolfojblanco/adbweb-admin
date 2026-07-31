"""
URL routing for the SEO module.

All SEO endpoints are mounted under ``/api/seo/`` by the project
root ``urls.py``.
"""
from rest_framework.routers import DefaultRouter

from .views import (
    LighthouseResultViewSet,
    SEOAuditViewSet,
    SEOIssueViewSet,
    SEOPageViewSet,
    SEORecommendationViewSet,
    SEOScoreViewSet,
    WebsiteViewSet,
)

router = DefaultRouter()
router.register(r"websites", WebsiteViewSet, basename="seo-website")
router.register(r"audits", SEOAuditViewSet, basename="seo-audit")
router.register(r"pages", SEOPageViewSet, basename="seo-page")
router.register(r"issues", SEOIssueViewSet, basename="seo-issue")
router.register(
    r"recommendations",
    SEORecommendationViewSet,
    basename="seo-recommendation",
)
router.register(r"scores", SEOScoreViewSet, basename="seo-score")
router.register(r"lighthouse", LighthouseResultViewSet, basename="seo-lighthouse")

urlpatterns = router.urls
