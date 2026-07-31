"""
DRF serializers for the SEO module.

Structure only: real field-level validation will be filled in once the
API surface is finalized.
"""
from rest_framework import serializers

from .models import (
    LighthouseResult,
    SEOAudit,
    SEOIssue,
    SEOPage,
    SEORecommendation,
    SEOScore,
    Website,
)


class WebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = "__all__"


class SEOAuditSerializer(serializers.ModelSerializer):
    website_name = serializers.CharField(source="website.name", read_only=True)

    class Meta:
        model = SEOAudit
        fields = "__all__"


class SEOPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SEOPage
        fields = "__all__"


class SEOIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SEOIssue
        fields = "__all__"


class SEORecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SEORecommendation
        fields = "__all__"


class SEOScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = SEOScore
        fields = "__all__"


class LighthouseResultSerializer(serializers.ModelSerializer):
    page_url = serializers.CharField(source="page.url", read_only=True)

    class Meta:
        model = LighthouseResult
        fields = "__all__"
