"""
DRF views for the SEO module.

Views are intentionally thin: every action is a one-liner that
delegates to :mod:`apps.seo.services`. There is no business
logic in this file.
"""
from __future__ import annotations

from uuid import UUID

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from . import services
from .models import (
    LighthouseResult,
    SEOAudit,
    SEOIssue,
    SEOPage,
    SEORecommendation,
    SEOScore,
    Website,
)
from .permissions import IsSeoAdmin
from .serializers import (
    LighthouseResultSerializer,
    SEOAuditSerializer,
    SEOIssueSerializer,
    SEOPageSerializer,
    SEORecommendationSerializer,
    SEOScoreSerializer,
    WebsiteSerializer,
)


class WebsiteViewSet(viewsets.ModelViewSet):
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSeoAdmin]
    search_fields = ["name", "domain"]
    ordering_fields = ["name", "created_at"]


class SEOAuditViewSet(viewsets.ModelViewSet):
    """CRUD + ``run`` / ``cancel`` actions. All work happens in services."""

    queryset = SEOAudit.objects.select_related("website").all()
    serializer_class = SEOAuditSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSeoAdmin]
    search_fields = ["target_url", "website__name"]
    ordering_fields = ["created_at", "status"]
    filterset_fields = ["status", "website"]

    @action(detail=True, methods=["post"], url_path="run")
    def run(self, request, pk=None):
        services.enqueue_audit(UUID(str(pk)))
        return Response(
            {"detail": "Auditoría encolada."},
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=["post"], url_path="crawl")
    def crawl(self, request, pk=None):
        services.enqueue_crawl(UUID(str(pk)))
        return Response(
            {"detail": "Crawl encolado."},
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        audit = services.cancel_audit(UUID(str(pk)))
        return Response(SEOAuditSerializer(audit).data)


class SEOPageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SEOPage.objects.all()
    serializer_class = SEOPageSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSeoAdmin]
    filterset_fields = ["audit", "status_code", "is_indexable"]


class SEOIssueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SEOIssue.objects.all()
    serializer_class = SEOIssueSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSeoAdmin]
    filterset_fields = ["page", "severity", "category"]


class SEORecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SEORecommendation.objects.all()
    serializer_class = SEORecommendationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSeoAdmin]
    filterset_fields = ["page", "priority"]


class SEOScoreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SEOScore.objects.all()
    serializer_class = SEOScoreSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSeoAdmin]
    filterset_fields = ["audit"]


class LighthouseResultViewSet(viewsets.ReadOnlyModelViewSet):
    """List Lighthouse runs and trigger new ones.

    Filtering is supported on ``page`` and ``page__audit``. To
    enqueue a new run, POST ``{"page_id": "<uuid>"}`` to the
    ``run`` action.
    """

    queryset = LighthouseResult.objects.select_related("page").all()
    serializer_class = LighthouseResultSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSeoAdmin]
    filterset_fields = ["page", "page__audit"]
    ordering_fields = ["run_at", "performance_score"]

    @action(detail=False, methods=["post"], url_path="run")
    def run(self, request):
        page_id = request.data.get("page_id")
        if not page_id:
            return Response(
                {"detail": "page_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            services.enqueue_lighthouse(UUID(str(page_id)))
        except ValueError:
            return Response(
                {"detail": "page_id must be a valid UUID."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"detail": "Lighthouse encolado."},
            status=status.HTTP_202_ACCEPTED,
        )
